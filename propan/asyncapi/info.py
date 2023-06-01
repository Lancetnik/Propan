from pydantic import BaseModel, Field


class AsyncAPIInfo(BaseModel):
    title: str
    version: str = Field(default="1.0.0")
    description: str = ""
