# example from https://lightning.ai/docs/pytorch/stable/starter/introduction.html

import os
from torch import optim, nn
from torchvision.datasets import MNIST
from torchvision.transforms import ToTensor
from torch.utils.data import DataLoader
import lightning as L


from configpy.configure import ConfigBuild


# define the LightningModule
class LitExperiment(L.LightningModule):
    def __init__(self, trainer, dataloader,  encoder, decoder):
        super().__init__()
        self.trainer = trainer
        self.dataloader = dataloader
        self.encoder = encoder
        self.decoder = decoder

    def training_step(self, batch, batch_idx):
        # training_step defines the train loop.
        # it is independent of forward
        x, y = batch
        x = x.view(x.size(0), -1)
        z = self.encoder(x)
        x_hat = self.decoder(z)
        loss = nn.functional.mse_loss(x_hat, x)
        # Logging to TensorBoard (if installed) by default
        self.log("train_loss", loss)
        return loss

    def configure_optimizers(self):
        optimizer = optim.Adam(self.parameters(), lr=1e-3)
        return optimizer

    def run(self):
        self.trainer.fit(model=self, train_dataloaders=self.dataloader)


# Your Config

experiment = ConfigBuild(obj=LitExperiment,
                         trainer=ConfigBuild(obj=L.Trainer,
                                             limit_train_batches=100,
                                             max_epochs=1),
                         dataloader=ConfigBuild(obj=DataLoader,
                                                dataset=ConfigBuild(obj=MNIST,
                                                                    root=os.getcwd(),
                                                                    download=True,
                                                                    transform=ToTensor()
                                                                    )),
                         encoder=ConfigBuild(obj=nn.Sequential,
                                             __args__=[ConfigBuild(obj=nn.Linear,
                                                                   in_features=28*28,
                                                                   out_features=64),
                                                       ConfigBuild(
                                                           obj=nn.ReLU),
                                                       ConfigBuild(obj=nn.Linear,
                                                                   in_features=64,
                                                                   out_features=3)]),

                         decoder=ConfigBuild(obj=nn.Sequential,
                                             __args__=[ConfigBuild(obj=nn.Linear,
                                                                   in_features=3,
                                                                   out_features=64),
                                                       ConfigBuild(
                                                           obj=nn.ReLU),
                                                       ConfigBuild(obj=nn.Linear,
                                                                   in_features=64,
                                                                   out_features=28*28)]))


if __name__ == "__main__":
    experiment.to_json('./mnist.json')
    # call the config
    exp = experiment()
    exp.run()
