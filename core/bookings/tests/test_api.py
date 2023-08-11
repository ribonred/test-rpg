import pytest
from rest_framework.test import APIClient
from rest_framework import status
from core.bookings.models import BookingEvent
from core.rooms.models import Room
from django.urls import reverse
from freezegun import freeze_time


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestEvent:
    event_url = reverse("bookingevent")

    def test_list_booking_events(self, api_client, setup_data, booking_event):
        response = api_client.get(self.event_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 4

    def test_create_booking_event(self, api_client, setup_data):
        room = Room.objects.first()
        with freeze_time("2022-12-31"):
            data = {
                "room_id": room.id,
                "hotel_id": room.hotel.id,
                "night_of_stay": "2022-12-31",
                "rpg_status": BookingEvent.RPGStatus.BOOKING,
            }
            response = api_client.post(self.event_url, data, format="json")
            response_data = response.json()
            assert response.status_code == status.HTTP_201_CREATED
            assert BookingEvent.objects.count() == 1
            assert response_data["room_id"] == room.id
            assert response_data["timestamp"] == "2022-12-31T00:00:00Z"
