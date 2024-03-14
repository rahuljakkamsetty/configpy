# configpy
A repo that provides a very custom data structure called "Configure/ConfigBuild" especially useful to setup the configuration of deep learning (DL) models.

Using this your deep-learning model config file would look below. 

```
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

```

This configuration file style offers a comprehensive overview of your deep learning experiments, facilitating the swift identification and fine-tuning of hyperparameters. It greatly enhances the ease of gaining intuition about your DL experiment. 

## Installation
Clone this repo and install using pip.

```
pip install git+ssh:git@github.com:rahuljakkamsetty/configpy.git
```
## Usage

Import the Configure or ConfigBuild class from configpy and start using them in your config file. A simple example would be as below.

```
from configpy import ConfigBuild

def multiply(a, b):
    return a * b 

def add(a,b):
    return a + b

def subtract(a, b):
    return a - b

myconfig = ConfigBuild(obj = add,
                        a = 10, 
                        b = ConfigBuild(obj = subtract,
                                        a = 10, b = ConfigBuild(obj = multiply,
                                                            a = 4,
                                                            b = 2)))


if __name__ == "__main__":
    myconfig()

```
In the above example, myconfig() call would call all the nested operations and return the output of calcuation. 

### Keywords in the configpy
   1. obj
   2. self_build
   3. \_\_args\_\_

