from typing import Any

from common.application.interfaces.repositories.key_value_store import (
    IKeyValueStore,
)
from common.infrastructure.database.redis.redis import RedisDatabase
from common.infrastructure.database.redis.repositories.key_value_store import (
    RedisKeyValueStore,
)
from common.infrastructure.database.sqlalchemy.database import Database
from common.infrastructure.database.sqlalchemy.session_factory import (
    ISessionFactory,
    MakerSessionFactory,
)
from common.infrastructure.serializers.serializer import ISerializer


def provide_maker_session_factory(database: Database) -> ISessionFactory:
    return MakerSessionFactory(database.get_session_maker())


def redis_key_value_store_provider(
    redis: RedisDatabase, serializer: ISerializer[Any], namespace: str
) -> IKeyValueStore[Any]:
    return RedisKeyValueStore(redis.get_client(), serializer, namespace)
