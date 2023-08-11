from typing import Literal, Protocol
import pandas as pd
from pydantic import BaseModel

from validator import ResponseProtocol


class ResponseHandlerProtocol(Protocol):
    validator_class: BaseModel | None = None
    validated_data: ResponseProtocol | None = None
    response: dict | list = {}

    def __init__(
        self,
        data_key="results",
        pagination_key="next",
        validator_class: BaseModel | None = None,
    ):
        ...

    @property
    def response_data(self) -> dict:
        ...

    @property
    def response_data_dict(self) -> dict:
        ...

    def validate(self):
        ...


class ProcessorProtocol(Protocol):
    def __init__(self, response_handler: ResponseHandlerProtocol):
        ...

    def process(self) -> list[dict]:
        ...


class ResponseHandler(ResponseHandlerProtocol):
    def __init__(
        self,
        data_key="results",
        pagination_key="next",
        validator_class: BaseModel | None = None,
    ):
        self.data_key = data_key
        self.pagination_key = pagination_key
        self.validator_class = validator_class

    def validate(self):
        self.validated_data: ResponseProtocol = self.validator_class(**self.response)

    @property
    def response_data(self):
        return self.validated_data.get_data()

    @property
    def response_data_dict(self):
        return self.validated_data.get_data_dict()


class BaseProcessor(ProcessorProtocol):
    def __init__(self, response_handler: ResponseHandlerProtocol):
        self.response_handler = response_handler

    def get_dataframe(self):
        data = self.response_handler.response_data_dict
        df = pd.DataFrame.from_records(data)
        if df.empty:
            return df
        df.drop_duplicates(subset='id', keep='first', inplace=True)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["month"] = df["timestamp"].dt.month
        df["year"] = df["timestamp"].dt.year
        df["day"] = df["timestamp"].dt.day
        return df


class DailyProcessor(BaseProcessor):
    def process(self):
        df = self.get_dataframe()
        if df.empty:
            return df
        df = df.groupby(["year", "month", "day"]).size().reset_index(name="event_count")
        return df


class MonthlyProcessor(BaseProcessor):
    def __init__(self, response_handler: ResponseHandlerProtocol):
        self.response_handler = response_handler

    def process(self):
        df = self.get_dataframe()
        if df.empty:
            return df
        df = df.groupby(["year", "month"]).size().reset_index(name="event_count")
        df["day"] = 1
        return df


class XclientProcessorFactory:
    def get_processor(period: Literal["day", "month"]):
        match period:
            case "day":
                return DailyProcessor
            case "month":
                return MonthlyProcessor
