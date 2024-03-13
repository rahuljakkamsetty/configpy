"""Contains the Configuration Data structures which can be used to write more readable config."""



from typing import Any, NewType, Optional
from collections.abc import Sequence
from collections import OrderedDict
from typing_extensions import Self
import json
from copy import deepcopy
import inspect


Path = NewType('Path', str)


def load_json(path: "Path") -> Any:
    """loads a json file.

    Parameters:
    -----------
    path: file path of json to be loaded.

    """
    with open(path, 'r+') as f:
        data = json.load(f)
    return data


def write_json(path: Path, data: Any) -> None:
    """writes data to a json file.

    Parameters:
    -----------
    path: file path of json to be saved.
    data: data to be dumped to json file.

    """
    assert path.endswith(
        '.json'), f"invalid path {path}, path should end with '.json'"
    with open(path, 'w+') as f:
        json.dump(data, f, indent=4)


class Parameters(OrderedDict):
    def __str__(self) -> str:
        k = 'key'
        v = 'argument'
        head = (f"{k:^18}|{v:^18}")+"\n"
        div = (f"-"*37)+"\n"
        lines = ''
        for k, v in self.items():
            lines += (f"{k:^18}|{v:^18}")+"\n"
        return head+div+lines


class Configure(dict):
    """
    The Configure class which helps to create a meaningful configuration file for Models.

    for e.g. say we have following methods.
    ```python

    def mulitply(a, b):
        return a * b 

    def add(a,b):
        return a + b

    def subtract(a, b):
        return a - b
    ```

    Now you can write a configuration which performs multiplication, subtraction and then addition in the following way

    ```python
    myconfig = Configure(obj = add,
                        self_build = True, 
                        a = 10, 
                        b = Configure(obj = subtract,
                                    self_build = True,
                                        a = 15, b = Configure(obj = multiply,
                                                            self_build = True,
                                                            a = 2,
                                                            b = 2)))
    ```
    or 

    ```python
    myconfig = ConfigBuild(obj = add,
                        a = 10, 
                        b = ConfigBuild(obj = subtract,
                                        a = 15, b = ConfigBuild(obj = multiply,
                                                            a = 2,
                                                            b = 2)))
    ```
    and finally call
    ```python
    myconfig()
    ``` 
    """

    internal_keys = ['self_build']

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def __self_build__(self):
        if self.get('self_build', None):
            self.pop('self_build')
            for key, value in self.items():
                if isinstance(value, Configure):
                    if 'obj' in value:
                        self[key] = value()
                if isinstance(value, Sequence) and not isinstance(value, str):
                    elem_type = type(value)
                    self[key] = elem_type(
                        [i() if isinstance(i, Configure) else i for i in value])

    def __setattr__(self, __name: str, __value: Any) -> None:
        self[__name] = __value

    def __getattribute__(self, __name: str) -> Any:
        return super().__getattribute__(__name)

    def __call__(self, *args: Any, **kwds: Any) -> Any:

        obj = self.pop('obj', None)
        if obj:
            self.__self_build__()
            arguments = dict(**self)
            arguments.update(kwds)
            return obj(*args, **arguments)
        else:
            raise AttributeError(
                f"No Class or Method is available. For e.g. pass obj='Your method/class' as an argument")

    def flatten(self, prev_key: Optional[str] = None):
        """
        Flattens the nested configure object and retruns as ordered dict.
        """

        outp = Parameters()
        for key, value in self.items():
            key_ = key
            if prev_key:
                key = f"{prev_key}_{key}"
            if isinstance(value, Configure):
                outp.update(value.flatten(key))
            else:
                if key_ not in self.internal_keys:
                    if hasattr(value, '__name__'):
                        outp[key] = value.__name__
                    else:
                        outp[key] = value
        return outp

    def serialize(self):
        """
        Serializes the configure object to create JSON serializable configure object.
        """

        for key, value in self.items():
            if isinstance(value, Configure):
                value.serialize()
            if key == 'obj':
                new_obj = inspect.getmodule(value).__name__
                self[key] = f"{new_obj}.{value.__name__}"

    def dump(self, path: Path):
        """
        Dumps the configure object to a JSON file.

        Parameters:
        -----------
        path: Path where the JSON file has to be stored including it's name.

        """
        clone = self.clone()
        clone.serialize()
        write_json(path=path, data=clone)

    def clone(self) -> Self:
        """
        returns a copy with new address on the memory.
        """
        return deepcopy(self)


class ConfigBuild(Configure):
    def __init__(self, **kwargs) -> None:
        self['self_build'] = True
        super().__init__(**kwargs)
