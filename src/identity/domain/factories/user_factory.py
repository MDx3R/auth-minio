from common.domain.uuid_generator import IUUIDGenerator
from identity.domain.entity.user import User
from identity.domain.interfaces.user_factory import IUserFactory


class UserFactory(IUserFactory):
    def __init__(self, uuid_generator: IUUIDGenerator) -> None:
        self.uuid_generator = uuid_generator

    def create(self, username: str, password: str) -> User:
        return User.create(self.uuid_generator.create(), username, password)
