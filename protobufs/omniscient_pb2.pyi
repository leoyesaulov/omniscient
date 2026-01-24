from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Payment(_message.Message):
    __slots__ = ("store", "amount")
    STORE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    store: str
    amount: int
    def __init__(self, store: _Optional[str] = ..., amount: _Optional[int] = ...) -> None: ...

class PaymentResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class DateQuery(_message.Message):
    __slots__ = ("start_date", "stop_date")
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    STOP_DATE_FIELD_NUMBER: _ClassVar[int]
    start_date: str
    stop_date: str
    def __init__(self, start_date: _Optional[str] = ..., stop_date: _Optional[str] = ...) -> None: ...

class QueryResponse(_message.Message):
    __slots__ = ("success", "amount")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    amount: int
    def __init__(self, success: bool = ..., amount: _Optional[int] = ...) -> None: ...
