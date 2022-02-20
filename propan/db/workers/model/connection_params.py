from dataclasses import dataclass


@dataclass
class Connection:
    user: str
    password: str
    host: str
    name: str
    port: str
