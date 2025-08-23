from uuid import UUID, uuid4

from common.domain.uuid_generator import IUUIDGenerator


class UUID4Generator(IUUIDGenerator):
    def create(self) -> UUID:
        return uuid4()
