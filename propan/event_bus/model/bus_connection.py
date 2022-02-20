from dataclasses import dataclass


@dataclass
class ConnectionData:
    host: str
    login: str
    password: str
    virtualhost: str
