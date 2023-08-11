import aiohttp

from aiohttp.client_exceptions import ClientResponseError, ClientConnectionError
from fastapi import HTTPException
from config import Settings
from datetime import datetime
from process import ResponseHandlerProtocol, ProcessorProtocol
import asyncio
import pandas as pd
from pydantic import BaseModel, ValidationError
from logs import setup_logger


logger = setup_logger(__name__)


def exception_handler(func):
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except ClientResponseError as e:
            logger.error(
                f"client error {e.status}",
            )
            self._response = pd.DataFrame()
            raise HTTPException(status_code=400, detail="provider error")
        except ClientConnectionError:
            logger.error(
                "client connection error",
            )
            self._response = pd.DataFrame()
            raise HTTPException(status_code=400, detail="client connection error")
        except ValidationError as e:
            logger.error(
                f"validation error {e}",
            )
            self._response = pd.DataFrame()
            raise HTTPException(status_code=400, detail="provider schema error")

    return wrapper


class BaseProvider:
    _response: pd.DataFrame | None = None
    _rate_limit_min = None
    _call_status: str

    def __init__(
        self,
        name,
        base_url,
        headers: dict = {},
        concurrency: int = 10,
    ):
        self.name = name
        self.base_url = base_url
        self.headers = headers
        self.concurrency = concurrency

    def get_semaphores(self):
        return asyncio.Semaphore(self.concurrency)

    def build_processed_response(self, builder: BaseModel):
        generated_dict = self._response.to_dict(orient="records")
        return builder(data=generated_dict, status="success")

    @property
    def rate_limit_min(self):
        return self._rate_limit_min

    @rate_limit_min.setter
    def rate_limit_min(self, value):
        self._rate_limit_min = value

    async def request(self, path, method: str, data: dict = {}):
        URL = f"{self.base_url}{path}"
        async with aiohttp.ClientSession(
            raise_for_status=True, headers=self.headers
        ) as client:
            req = getattr(client, method.lower())
            kwargs_key = {
                "get": "params",
                "post": "data",
            }
            options = {kwargs_key[method.lower()]: data}
            response = await req(URL, **options)
            return await response.json()

    def set_response_handler(self, handler: ResponseHandlerProtocol):
        self.handler: ResponseHandlerProtocol = handler

    async def handle_response(self, response) -> ResponseHandlerProtocol:
        if not self.handler:
            raise NotImplementedError("Response handler not set")
        self.handler.response = response
        self.handler.validate()
        return self.handler

    def calculate_sleep_time(self, request_count: int):
        time_to_take = request_count / self.rate_limit_min
        seconds = time_to_take * 60
        return seconds / max(request_count, 1) * self.concurrency

    async def bound_request(self, sem, path, method, params, sleep_time=0.6):
        # Getter function with semaphore.
        async with sem:
            await asyncio.sleep(sleep_time)
            return await self.request(path, method, params)


class XclientApi(BaseProvider):
    rate_limit_min = 200

    def year_query_builder(self, year: int):
        # go to very first date of the year
        start_date = datetime(year, 1, 1)
        # go to very last date of the year
        end_date = datetime(year, 12, 31)
        return {
            "event_from": start_date.strftime("%Y-%m-%d"),
            "event_to": end_date.strftime("%Y-%m-%d"),
        }

    @exception_handler
    async def get_hotel_data(
        self,
        hotel_id: int,
        year: int,
        processor: ProcessorProtocol,
        handlepaginated: bool = False,
    ) -> None:
        path = "/api/events/"
        params = {"hotel_id": hotel_id, "page_size": "250"}
        if year:
            params.update(self.year_query_builder(year))

        response = await self.request(path, "GET", params)
        handled_response = await self.handle_response(response)
        if not handlepaginated:
            processed_response = processor(handled_response)
            self._response = processed_response.process()
        else:
            if handled_response.validated_data.get_page_counter() > 1:
                pages = handled_response.validated_data.get_page_counter()
                sem = self.get_semaphores()
                tasks = set()
                print(pages, "page")
                sleep_time = self.calculate_sleep_time(pages)
                params.update({"page": 1})
                for _ in range(pages):
                    params["page"] = params["page"] + 1
                    modified_params = params.copy()
                    task = asyncio.create_task(
                        self.bound_request(
                            sem, path, "GET", modified_params, sleep_time=sleep_time
                        )
                    )
                    tasks.add(task)

                data = await asyncio.gather(*tasks)
                collected_result = []
                for dresponse in data:
                    handled = await self.handle_response(dresponse)
                    collected_result += handled.response_data
                handled_response.validated_data.results.extend(collected_result)
            processed_response = processor(handled_response)
            self._response = processed_response.process()


class ProviderFactory:
    @staticmethod
    def get_xclient_api(
        from_env: bool = True, name: str | None = None, base_url: str | None = None
    ) -> XclientApi:
        if not from_env and (name is None or base_url is None):
            raise ValueError("name and base_url must be provided")
        if from_env:
            settings = Settings()
            if hasattr(settings, "xclient"):
                client_settings = settings.xclient
                return XclientApi(client_settings.name, client_settings.base_url)
            else:
                raise NotImplementedError("Provider not implemented")
        else:
            return XclientApi(name, base_url)
