from sqlalchemy.future import select
from sqlalchemy import insert
from sqlalchemy.sql.expression import Delete, Update, Insert, bindparam

from propan.db.workers.model.model.recorder import ARUsecase
from propan.db.workers.implementation.alchemy.engine import AlchemyAsyncEngine


class AlchemyRepository(ARUsecase):
    _engine: AlchemyAsyncEngine

    def __init__(self, engine: AlchemyAsyncEngine):
        self._engine = engine

    class Decorators:
        @classmethod
        def session_mixin(cls, func):
            async def wrapped(self, *args, **kwargs):
                return await self._engine.get_session(func)(self, *args, **kwargs)
            return wrapped


    @Decorators.session_mixin
    async def delete(self, model, *args, session, **kwargs):
        stmt = Delete(model).where(*args, **kwargs)
        await session.execute(stmt)
        await session.commit()


    @Decorators.session_mixin
    async def get(self, model, *args, session, **kwargs):
        stmt = select(model).filter(*args, **kwargs)
        r = await session.execute(stmt)
        return r.scalars().fetchall()


    @Decorators.session_mixin
    async def create(self, item, session):
        session.add(item)
        await session.commit()

    @Decorators.session_mixin
    async def create_all(self, items, session):
        session.add_all(items)
        await session.commit()


    @Decorators.session_mixin
    async def update(self, items, session):
        if isinstance(items, list) is False:
            items = [items]

        model = type(items[0])
        ids = [i.id for i in items]
        fields_to_update = list(filter(lambda x: not x.startswith('_'), items[0].__dict__.keys()))

        stmt = Update(model).where(model.id == bindparam('id')).values({
            field: bindparam(field) for field in fields_to_update
        })

        await session.execute(stmt, [
            {field: item.__dict__[field] for field in fields_to_update}
            for item in items
        ])


    @Decorators.session_mixin
    async def get_or_create(self, model, *args, session, **kwargs):
        stmt = select(model).filter_by(**kwargs)
        result = await session.execute(stmt)

        if r := result.first():
            return r[0], False

        else:
            obj = model(**kwargs)
            session.add(obj)
            await session.commit()
            return obj, True