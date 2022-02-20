from typing import Protocol, Dict

from .proxie_data import FromSettings


class ProxyUsecase(Protocol):
    def __init__(self, data: FromSettings):
        raise NotImplementedError()

    def get_proxy(self) -> Dict[str, str]:
        raise NotImplementedError()

    def switch(self) -> bool:
        raise NotImplementedError()
