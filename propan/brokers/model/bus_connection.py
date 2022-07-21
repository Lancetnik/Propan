from typing import Optional

from dataclasses import dataclass


@dataclass
class ConnectionData:
    host: str
    port: int
    login: Optional[str] = None
    password: Optional[str] = None
    virtualhost: str = "/"
