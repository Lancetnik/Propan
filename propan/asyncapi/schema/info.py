from typing import Any, Callable, Iterable, Optional, Type

from pydantic import AnyHttpUrl, BaseModel

from propan._compat import (
    CoreSchema,
    GetJsonSchemaHandler,
    JsonSchemaValue,
    general_plain_validator_function,
    is_installed,
)
from propan.log import logger

if is_installed("email_validator"):
    from pydantic import EmailStr
else:  # pragma: no cover
    # NOTE: EmailStr mock was copied from the FastAPI
    # https://github.com/tiangolo/fastapi/blob/master/fastapi/openapi/models.py#24
    class EmailStr(str):  # type: ignore
        @classmethod
        def __get_validators__(cls) -> Iterable[Callable[..., Any]]:
            yield cls.validate

        @classmethod
        def validate(cls, v: Any) -> str:
            logger.warning(
                "email-validator bot installed, email fields will be treated as str.\n"
                "To install, run: pip install email-validator"
            )
            return str(v)

        @classmethod
        def _validate(cls, __input_value: Any, _: Any) -> str:
            logger.warning(
                "email-validator bot installed, email fields will be treated as str.\n"
                "To install, run: pip install email-validator"
            )
            return str(__input_value)

        @classmethod
        def __get_pydantic_json_schema__(
            cls,
            core_schema: CoreSchema,
            handler: GetJsonSchemaHandler,
        ) -> JsonSchemaValue:
            return {"type": "string", "format": "email"}

        @classmethod
        def __get_pydantic_core_schema__(
            cls,
            source: Type[Any],
            handler: Callable[[Any], CoreSchema],
        ) -> JsonSchemaValue:
            return general_plain_validator_function(cls._validate)


class Contact(BaseModel):
    name: str
    url: Optional[AnyHttpUrl] = None
    email: Optional[EmailStr] = None


class License(BaseModel):
    name: str
    url: Optional[AnyHttpUrl] = None


class Info(BaseModel):
    title: str
    version: str = "1.0.0"
    description: str = ""
    termsOfService: Optional[AnyHttpUrl] = None
    contact: Optional[Contact] = None
    license: Optional[License] = None
