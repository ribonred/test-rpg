from fastapi import FastAPI, Query
from clients import ProviderFactory
from config import Settings
from process import ResponseHandler, XclientProcessorFactory
from validator import ClientXResponse
from typing import Literal
import uvicorn
import time
from pydantic import BaseModel


class ResultSchema(BaseModel):
    year: int
    month: int
    day: int | None
    event_count: int


class DashboardResponse(BaseModel):
    data: list[ResultSchema] | list


app = FastAPI(docs_url="/", redoc_url="/redoc")


@app.get("/api/dashboard")
async def read_dashboard(
    hotel_id: str = Query(...),
    year: int = Query(...),
    period: Literal["day", "month"] = Query(...),
) -> DashboardResponse:
    provider = ProviderFactory.get_xclient_api()
    handler = ResponseHandler(validator_class=ClientXResponse)
    provider.set_response_handler(handler)
    start_time = time.time()
    processor = XclientProcessorFactory.get_processor(period)
    await provider.get_hotel_data(
        hotel_id, year, processor=processor, handlepaginated=True
    )
    print("--- %s seconds ---" % (round(time.time() - start_time, 2)))
    return provider.build_processed_response(DashboardResponse)


if __name__ == "__main__":
    settings = Settings()
    uvicorn.run("main:app", port=settings.port, reload=True, host=settings.host)
