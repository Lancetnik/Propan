from typing import Optional

from pydantic import BaseModel


class ConnectionData(BaseModel):
    host: str
    port: int
    login: Optional[str] = None
    password: Optional[str] = None
    virtualhost: str = "/"
