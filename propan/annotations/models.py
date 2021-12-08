import json

from pydantic import BaseModel


class MessageModel(BaseModel):
    def __init__(self, json_like: str):
        data = json.loads(json_like)
        super().__init__(**data)
