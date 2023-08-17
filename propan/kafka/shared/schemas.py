import ssl
from asyncio import AbstractEventLoop
from typing import List, Literal, Optional, TypedDict, Union

from aiokafka.abc import AbstractTokenProvider


class ConsumerConnectionParams(TypedDict, total=False):
    bootstrap_servers: Union[str, List[str]]
    loop: Optional[AbstractEventLoop]
    client_id: str
    request_timeout_ms: int
    retry_backoff_ms: int
    metadata_max_age_ms: int
    security_protocol: Literal[
        "SSL",
        "PLAINTEXT",
    ]
    api_version: str
    connections_max_idle_ms: int
    sasl_mechanism: Literal[
        "PLAIN",
        "GSSAPI",
        "SCRAM-SHA-256",
        "SCRAM-SHA-512",
        "OAUTHBEARER",
    ]
    sasl_plain_password: Optional[str]
    sasl_plain_username: Optional[str]
    sasl_kerberos_service_name: str
    sasl_kerberos_domain_name: Optional[str]
    ssl_conext: Optional[ssl.SSLContext]
    sasl_oauth_token_provider: Optional[AbstractTokenProvider]
