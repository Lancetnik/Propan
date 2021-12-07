from typing import Protocol

from propan.logger.model.usecase import LoggerUsecase
from propan.fetch.proxy.model.usecase import ProxyUsecase


class FetcherUsecase(Protocol):
    def __init__(self,
        proxy: ProxyUsecase, logger: LoggerUsecase,
        max_retries: int, sleep: int,
        timeout: int, headers: dict
    ):
        raise NotImplementedError()

    def __aenter__(self, *args, **kwargs):
        raise NotImplementedError()

    def __aexit__(self):
        raise NotImplementedError()

    def __enter__(self, *args, **kwargs):
        raise NotImplementedError()

    def __exit__(self):
        raise NotImplementedError()

    def get(self, url, *args, session, **kwargs):
        raise NotImplementedError()

    def post(self, url, *args, session, **kwargs):
        raise NotImplementedError()

    def get_json(self, url, *args, session, **kwargs):
        raise NotImplementedError()
