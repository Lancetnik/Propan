from typing import Optional

from pydantic import BaseModel, Field, HttpUrl

from propan._compat import is_installed

if is_installed("email_validator"):
    from pydantic import EmailStr
else:  # pragma: no cover
    EmailStr = str  # type: ignore


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
