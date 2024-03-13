"""Some utility functions."""

from typing import NewType, Any
import json


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