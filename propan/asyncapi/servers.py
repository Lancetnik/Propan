from pydantic import BaseModel


class AsyncAPIServer(BaseModel):
    url: str
    protocol: str
