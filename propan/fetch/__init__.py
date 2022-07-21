from propan.fetch.fetcher.adapter.async_adapter import AsyncFetcherImplementation
from propan.fetch.proxy.adapter.async_adapter import AsyncProxyAdapter
from propan.fetch.user_agent.getter import UserAgentFabric


Fetcher = AsyncFetcherImplementation
Proxy = AsyncProxyAdapter
UserAgent = UserAgentFabric

__all__ = (
    'Fetcher',
    'Proxy',
    'UserAgent'
)