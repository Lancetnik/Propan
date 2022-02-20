from dataclasses import dataclass
from typing import Union, List


@dataclass
class FromSettings:
    proxy: Union[str, List[str]]

    def __init__(self, data):
        if not isinstance(data, str):
            if not isinstance(data, list):
                raise ValueError('Proxy must be str or list[str] type')
            elif not isinstance(data[0], str):
                raise ValueError('Proxy must be str or list[str] type')
        self.proxy = data
