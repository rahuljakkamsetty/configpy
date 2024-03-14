"""Contains the Configuration Data structures which can be used to write more readable config."""

# python imports
from typing import Any, Callable, Optional
from collections.abc import Sequence
from collections import OrderedDict
from typing_extensions import Self
from copy import deepcopy
import inspect
from importlib import import_module
import sys

# third-party imports

# internal imports
from configpy.utils import load_json, write_json, Path



class Parameters(OrderedDict):
    """
    An ordered dict of parameters.
    """
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

    def multiply(a, b):
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
            just_args = self.pop('__args__', None)
            if just_args:
                just_args = [i for i in just_args]
                args = [i for i in args]
                args.extend(just_args)
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

    def serialize(self) -> None:
        """
        Serializes the configure object to create JSON serializable configure object.
        """

        for key, value in self.items():
            if isinstance(value, Configure):
                value.serialize()
            if key == 'obj':
                new_obj = inspect.getmodule(value).__name__
                self[key] = f"{new_obj}.{value.__name__}"

    def dump(self, path: Path) -> None:
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
    
    def __repr__(self) -> str:
        dict_str = super().__repr__()
        dict_str = dict_str.replace("{", "(")
        dict_str = dict_str.replace("}", ")")
        dict_str = f"Configure{dict_str}"

        return dict_str

    @staticmethod
    def traverse_dict(data: dict) -> None:
        for key, value in data.items():
            if key == 'obj':
                data[key] = Configure.get_method(value)
            if isinstance(value, dict):
                if 'obj' in value:
                    data[key] = Configure(**value)
                    Configure.traverse_dict(data[key])

    @staticmethod
    def from_json(path: Path) -> Self:
        """
        Creates a configure object from the provided json file
        
        Parameters:
        -----------
        path: Path to json file.

        """

        data = load_json(path)
        Configure.traverse_dict(data)
        config = Configure(**data)
        return config

    @staticmethod
    def get_method(obj: str) -> Callable:
        """
        Given the string form of the method, this method return object of that method.
        """

        if "." in obj:
            module_names = obj.split('.')
            method_name = module_names[-1]
        else:
            module_names = ['builtins', obj]
            method_name = obj

        if module_names[0] == "__main__":
            module = sys.modules["__main__"]
        else:
            module = import_module(module_names[0])

            for sub_module_name in module_names[1:-1]:
                module = getattr(module, sub_module_name)

        method = getattr(module, method_name)

        return method


class ConfigBuild(Configure):
    """
    Inherits from the original Configure object. 
    Automatically builds the whole nested ConfigBuild objects in the config file.

    """
    def __init__(self, **kwargs) -> None:
        self['self_build'] = True
        super().__init__(**kwargs)
