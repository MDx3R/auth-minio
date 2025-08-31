from typing import ClassVar as _ClassVar

from google.protobuf import descriptor as _descriptor, message as _message

DESCRIPTOR: _descriptor.FileDescriptor

class IssueTokensRequest(_message.Message):
    __slots__ = ("user_id",)
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    def __init__(self, user_id: str | None = ...) -> None: ...

class RefreshTokensRequest(_message.Message):
    __slots__ = ("refresh_token",)
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    refresh_token: str
    def __init__(self, refresh_token: str | None = ...) -> None: ...

class IntrospectTokenRequest(_message.Message):
    __slots__ = ("access_token",)
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    def __init__(self, access_token: str | None = ...) -> None: ...

class RevokeTokenRequest(_message.Message):
    __slots__ = ("refresh_token",)
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    refresh_token: str
    def __init__(self, refresh_token: str | None = ...) -> None: ...

class AuthResponse(_message.Message):
    __slots__ = ("access_token", "refresh_token", "user_id")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    access_token: str
    refresh_token: str
    def __init__(
        self,
        user_id: str | None = ...,
        access_token: str | None = ...,
        refresh_token: str | None = ...,
    ) -> None: ...

class IntrospectionResponse(_message.Message):
    __slots__ = ("user_id", "username")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    username: str
    def __init__(
        self, user_id: str | None = ..., username: str | None = ...
    ) -> None: ...
