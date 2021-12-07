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
            return await self.switch_mobileproxy_space_ip(proxy)
        else:
            return False

    async def switch_mobileproxy_space_ip(self, proxy={}) -> bool:
        if not proxy:
            proxy = self.get_proxie()['https']

        pattern = r'http://(.+):(.+)@.+:(\d+)'
        result = re.match(pattern, proxy)
        login, password, port = result.group(1), result.group(2), result.group(3)

        url = f'https://mobileproxy.space/reload.html?login={login}&pass={password}&port={port}'

        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as response:
                if response.status == 200:
                    return True
                else:
                    return False