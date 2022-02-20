from .fetcher.adapter.async_adapter import AsyncFetcherImplementation
from .proxy.adapter.async_adapter import AsyncProxyAdapter
from .user_agent.getter import UserAgentFabric


Fetcher = AsyncFetcherImplementation
Proxy = AsyncProxyAdapter
UserAgent = UserAgentFabric

__all__ = (
    'Fetcher',
    'Proxy',
    'UserAgent'
)