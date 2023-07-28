from typing import Optional

from pydantic import AnyHttpUrl, BaseModel

from propan._compat import is_installed

if is_installed("email_validator"):
    from pydantic import EmailStr
else:  # pragma: no cover
    EmailStr = str  # type: ignore


class AsyncAPIContact(BaseModel):
    name: str
    url: Optional[AnyHttpUrl] = None
    email: Optional[EmailStr] = None


class AsyncAPILicense(BaseModel):
    name: str
    url: Optional[AnyHttpUrl] = None


class AsyncAPIInfo(BaseModel):
    title: str
    version: str = "1.0.0"
    description: str = ""
    termsOfService: Optional[AnyHttpUrl] = None
    contact: Optional[AsyncAPIContact] = None
    license: Optional[AsyncAPILicense] = None
