import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from clients import XclientApi
from main import app
import copy

client = TestClient(app)
mock_data = {
    "count": 0,
    "next": "http://127.0.0.1:8000/api/events/?page=2&page_size=250",
    "previous": None,
    "results": [
        {
            "room_id": "2e4fbe7c-01cb-471e-a961-ae5b00c76ab1",
            "hotel_id": 2607,
            "rpg_status": 2,
            "night_of_stay": "2023-08-11",
            "timestamp": "2023-08-11T07:38:15.068097Z",
            "id": 25,
        },
        {
            "room_id": "2e4fbe7c-01cb-471e-a961-ae5b00c76ab1",
            "hotel_id": 2607,
            "rpg_status": 1,
            "night_of_stay": "2023-08-11",
            "id": 1,
            "timestamp": "2023-08-11T07:37:36.086448Z",
        },
    ],
}
fail_mock_data = copy.deepcopy(mock_data)
fail_mock_data["results"][0].pop("id")
paginate_mock_data = copy.deepcopy(mock_data)
paginate_mock_data["count"] = 10


@pytest.mark.asyncio
async def test_read_dashboard():
    # Mock the request method of the provider
    with patch.object(XclientApi, "request", new=AsyncMock()) as request_mock:
        request_mock.return_value = mock_data
        # Call the function with test data
        response = client.get("/api/dashboard?hotel_id=test&year=2023&period=day")
        assert request_mock.call_count == 1

    # Assert that the function returns the correct response
    assert response.status_code == 200
    assert response.json() == {
        "data": [{"year": 2023, "month": 8, "day": 11, "event_count": 2}]
    }


@pytest.mark.asyncio
async def test_read_fail_schema_dashboard():
    # Mock the request method of the provider
    with patch.object(XclientApi, "request", new=AsyncMock()) as request_mock:
        request_mock.return_value = fail_mock_data
        # Call the function with test data
        response = client.get("/api/dashboard?hotel_id=test&year=2023&period=day")
    # Assert that the function returns the correct response
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_read_paginator_dashboard():
    # Mock the request method of the provider
    with patch.object(XclientApi, "request", new=AsyncMock()) as request_mock:
        request_mock.return_value = paginate_mock_data
        # Call the function with test data
        response = client.get("/api/dashboard?hotel_id=test&year=2023&period=day")
        # assert if provider handle recursive call for pagination
        # first call is read data count is 10 and provide a response with each result 2
        # so the provider will call 5 times, 1 for first call and 4 for pagination
        assert request_mock.call_count == 5

    # Assert that the function returns the correct response
    assert response.status_code == 200
