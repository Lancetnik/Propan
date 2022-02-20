from typing import List

from tortoise import Tortoise

from propan.db.workers.model.connection_params import Connection


async def init_tortoise(conn: Connection, ways_to_models: List[str]):
    await Tortoise.init(
        db_url=f'postgres://{conn.user}:{conn.password}@{conn.host}/{conn.name}',
        modules={'models': ways_to_models}
    )
