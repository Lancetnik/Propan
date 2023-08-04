from abc import abstractproperty
from typing import Optional, Tuple

from propan.asyncapi.schema.channels import Channel


class AsyncAPIOperation:
    @abstractproperty
    def name(self) -> str:
        raise NotImplementedError()

    def schema(self) -> Tuple[str, Optional[Channel]]:
        return self.name, None
