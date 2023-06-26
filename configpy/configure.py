"""Contains the Configuration Data structures which can be used to write more readable config.

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
myconfig = Configure(objekt = add,
                    self_build = True, 
                    a = 10, 
                    b = Configure(objekt = subtract,
                                self_build = True,
                                    a = 15, b = Configure(objekt = multiply,
                                                         self_build = True,
                                                         a = 2,
                                                         b = 2)))
```
or 

```python
myconfig = ConfigBuild(objekt = add,
                    a = 10, 
                    b = ConfigBuild(objekt = subtract,
                                    a = 15, b = ConfigBuild(objekt = multiply,
                                                         a = 2,
                                                         b = 2)))
```
and finally call

```python
myconfig()
```
"""

from typing import Any
from collections.abc import Sequence
from collections import OrderedDict


class Configure(dict):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def __self_build__(self):
        if self.get('self_build', None):
            self.pop('self_build')
            for key, value in self.items():
                if isinstance(value, Configure):
                    if 'objekt' in value:
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

        objekt = self.pop('objekt', None)
        if objekt:
            self.__self_build__()
            arguments = dict(**self)
            arguments.update(kwds)
            return objekt(*args, **arguments)
        else:
            raise AttributeError(
                f"No Class or Method is available. For e.g. pass objekt='Your method/class' as an argument")

    def flatten(self, prev_key=None):
        outp = OrderedDict()
        internal_keys = ['self_build']
        for key, value in self.items():
            key_ = key
            if prev_key:
                key = f"{prev_key}_{key}"
            if isinstance(value, Configure):
                outp.update(value.flatten(key))
            else:
                if key_ not in internal_keys:
                    if hasattr(value, '__name__'):
                        outp[key] = value.__name__
                    else:
                        outp[key] = value
        return outp


class ConfigBuild(Configure):
    def __init__(self, **kwargs) -> None:
        self['self_build'] = True
        super().__init__(**kwargs)
