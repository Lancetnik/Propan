from typing import Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class AsyncAPIContact(BaseModel):
    name: str
    url: HttpUrl
    email: Optional[EmailStr] = None


class AsyncAPILicense(BaseModel):
    name: str
    url: HttpUrl


class AsyncAPIInfo(BaseModel):
    title: str
    version: str = "1.0.0"
    description: str = ""
    terms: Optional[HttpUrl] = Field(
        default=None,
        alias="termsOfService",
    )
    contact: Optional[AsyncAPIContact] = None
    license: Optional[AsyncAPILicense] = None

    class Config:
        allow_population_by_field_name = True
