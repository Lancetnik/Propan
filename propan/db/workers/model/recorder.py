from typing import Protocol, NoReturn, Union

from .object import DbObject


class ARUsecase(Protocol):
    def create(self, item: DbObject) -> DbObject:
        raise NotImplementedError()

    def bulk_create(self, items: list[DbObject]) -> list[DbObject]:
        raise NotImplementedError()

    def update(self, item: DbObject) -> DbObject:
        raise NotImplementedError()

    def bulk_update(self, items: list[DbObject]) -> list[DbObject]:
        raise NotImplementedError()

    def update_or_create(self, item: DbObject) -> (DbObject, bool):
        raise NotImplementedError()

    def get(self, model, *args, **kwargs) -> DbObject:
        raise NotImplementedError()

    def get_or_create(self, model, *args, **kwargs) -> (DbObject, bool):
        raise NotImplementedError()

    def filter(self, model, *args, **kwargs) -> list[DbObject]:
        raise NotImplementedError()

    def delete(self, to_del: Union[DbObject, list[DbObject]]) -> NoReturn:
        raise NotImplementedError()
