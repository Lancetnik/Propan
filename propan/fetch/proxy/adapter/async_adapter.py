from random import choice
import re
from typing import Union, List

import aiohttp

from propan.config import settings
from propan.fetch.proxy.model.usecase import ProxyUsecase
from propan.fetch.proxy.model.proxie_data import FromSettings


class AsyncProxyAdapter(ProxyUsecase):
    def __init__(
        self, proxy: Union[List[str], str] = settings.PROXY,
        from_settings: FromSettings = None, is_switchable=False
    ):
        try:
            self.proxy = proxy or from_settings.proxy
        except AttributeError:
            raise ValueError('Needs to set `proxy` or `from settings`')
        self.is_switchable = is_switchable

    def get_proxy(self):
        if isinstance(self.proxy, list):
            return {'https': choice(self.proxy)}
        elif isinstance(self.proxy, str):
            return {'https': self.proxy}

    async def switch(self, proxy={}) -> bool:
        if self.is_switchable:
            return await self.get_proxy()
        else:
            return False
