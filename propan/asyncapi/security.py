from typing import Dict, Optional

from pydantic import BaseModel, Field, HttpUrl
from typing_extensions import Literal


class AsyncAPIOauthFlowObj(BaseModel):
    authorization_url: Optional[HttpUrl] = Field(
        default=None,
        alias="authorizationUrl",
    )
    token_url: Optional[HttpUrl] = Field(
        default=None,
        alias="tokenUrl",
    )
    refresh_url: Optional[HttpUrl] = Field(
        default=None,
        alias="refreshUrl",
    )
    scopes: Dict[str, str]


class AsyncAPIOauthFlows(BaseModel):
    implicit: Optional[AsyncAPIOauthFlowObj] = None
    password: Optional[AsyncAPIOauthFlowObj] = None
    client_credentials: Optional[AsyncAPIOauthFlowObj] = Field(
        default=None,
        alias="clientCredentials",
    )
    authorization_code: Optional[AsyncAPIOauthFlowObj] = Field(
        default=None,
        alias="authorizationCode",
    )


class AsyncAPISecuritySchemeComponent(BaseModel):
    type: Literal[
        "userPassword",
        "apikey",
        "X509",
        "symmetricEncryption",
        "asymmetricEncryption",
        "httpApiKey",
        "http",
        "oauth2",
        "openIdConnect",
        "plain",
        "scramSha256",
        "scramSha512",
        "gssapi",
    ]
    name: Optional[str] = None
    description: Optional[str] = None
    in_: Optional[str] = Field(
        default=None,
        alias="in",
    )
    scheme: Optional[str] = None
    bearer_format: Optional[str] = Field(
        default=None,
        alias="bearerFormat",
    )
    openid_connect_url: Optional[str] = Field(
        default=None,
        alias="openIdConnectUrl",
    )
    flows: Optional[AsyncAPIOauthFlows] = None
