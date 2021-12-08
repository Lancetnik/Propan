from random import choice
import re

import aiohttp

from propan.fetch.proxy.model.usecase import ProxyUsecase
from propan.fetch.proxy.model.proxie_data import FromSettings


class ProxyAsyncAdapter(ProxyUsecase):
    def __init__(self, proxy: FromSettings, is_switchable=False):
        self.proxy = proxy.proxy
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
