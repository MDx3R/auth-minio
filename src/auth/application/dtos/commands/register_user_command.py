from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterUserCommand:
    username: str
    password: str
