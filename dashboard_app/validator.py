from pydantic import BaseModel
from typing import Protocol
import math


class ResponseProtocol(Protocol):
    def has_more_data(self) -> bool:
        ...

    def get_data(self) -> list | dict:
        ...

    def get_page_counter(self) -> int:
        ...


class ClientXResult(BaseModel):
    room_id: str
    hotel_id: int
    rpg_status: int
    night_of_stay: str
    id: int
    timestamp: str


class ClientXResponse(BaseModel):
    count: int | None
    next: str | None
    previous: str | None
    results: list[ClientXResult]

    def has_more_data(self):
        return self.next is not None

    def get_data(self):
        return self.results

    def get_data_dict(self):
        return [result.model_dump() for result in self.results]

    def get_page_counter(self):
        return abs(math.ceil(self.count / max(len(self.results), 1)) - 1)
