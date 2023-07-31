from typing import Dict, Optional

from pydantic import AnyHttpUrl, BaseModel, Field
from typing_extensions import Literal


class OauthFlowObj(BaseModel):
    authorizationUrl: Optional[AnyHttpUrl] = None
    tokenUrl: Optional[AnyHttpUrl] = None
    refreshUrl: Optional[AnyHttpUrl] = None
    scopes: Dict[str, str]


class OauthFlows(BaseModel):
    implicit: Optional[OauthFlowObj] = None
    password: Optional[OauthFlowObj] = None
    clientCredentials: Optional[OauthFlowObj] = None
    authorizationCode: Optional[OauthFlowObj] = None


class SecuritySchemeComponent(BaseModel):
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
    bearerFormat: Optional[str] = None
    openIdConnectUrl: Optional[str] = None
    flows: Optional[OauthFlows] = None
