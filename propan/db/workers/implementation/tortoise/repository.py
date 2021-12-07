from typing import NoReturn, Union, Iterable

from tortoise.exceptions import DoesNotExist
from tortoise.queryset import QuerySet

from propan.db.workers.model.recorder import ARUsecase
from propan.db.workers.model.object import DbObject


class TortoiseRepository(ARUsecase):
    async def create(self, item: DbObject) -> DbObject:
        await item.save()
        return item

    async def bulk_create(self, model, items: Iterable[DbObject]) -> list[DbObject]:
        for item in items:
            await item.save()
        return items

    async def update(self, item: DbObject) -> DbObject:
        await item.save()
        return item

    async def bulk_update(self, items: Iterable[DbObject]) -> list[DbObject]:
        for ob in items:
            await ob.save()
        return items

    async def update_or_create(self, model, defaults=None, **kwargs) -> (DbObject, bool):
        try:
            obj = await model.get(**kwargs)
            for key, value in defaults.items():
                setattr(obj, key, value)
            await obj.save()
            return obj, False

        except DoesNotExist:
            kwargs.update(defaults)
            obj = model(**kwargs)
            await obj.save()
            return obj, True

    async def get(self, model, *args, **kwargs) -> DbObject:
        return await model.get(*args, **kwargs)

    async def get_or_create(self, model, *args, **kwargs) -> (DbObject, bool):
        return await model.get_or_create(*args, **kwargs)

    async def delete(self, to_del: Union[DbObject, QuerySet]) -> NoReturn:
        await to_del.delete()

    def filter(self, model, *args, **kwargs) -> QuerySet:
        return model.filter(*args, **kwargs)