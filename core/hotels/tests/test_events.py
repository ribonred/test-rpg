import pytest
from conftest import BookingEventFactory
from core.hotels.models import Hotel


@pytest.mark.django_db
def test_fixtures_data(setup_data):
    hotels = Hotel.objects.prefetch_related("rooms").all()
    assert hotels.count() == 2
    for hotel in hotels:
        assert hotel.rooms.count() == 5


@pytest.mark.django_db
def test_booking_event_creation(setup_data):
    room = Hotel.objects.prefetch_related("rooms").get(name="wellington").rooms.first()
    booking_event = BookingEventFactory.create(room=room)
    assert booking_event.room == room
