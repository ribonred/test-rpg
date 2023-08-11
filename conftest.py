import factory
import pytest
from core.hotels.models import Hotel
from core.rooms.models import Room, RoomAvailability
from core.bookings.models import BookingEvent
from faker import Faker

faker = Faker()


class HotelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Hotel

    name = factory.LazyAttribute(lambda x: faker.company())
    address = factory.LazyAttribute(lambda x: faker.address())
    phone = factory.LazyAttribute(lambda x: faker.phone_number())
    email = factory.LazyAttribute(lambda x: faker.email())
    website = factory.LazyAttribute(lambda x: faker.url())
    description = factory.LazyAttribute(lambda x: faker.text())


class RoomFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Room

    hotel = factory.SubFactory(HotelFactory)
    capacity = factory.LazyAttribute(lambda x: faker.random_int(min=1, max=4))
    room_type = factory.LazyAttribute(
        lambda x: faker.random_element(Room.RoomTypes.choices)
    )
    room_number = factory.Sequence(lambda n: n)


class RoomAvailabilityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RoomAvailability

    room = factory.SubFactory(RoomFactory)
    start_date = factory.LazyAttribute(
        lambda x: faker.date_between(start_date="-30d", end_date="today")
    )
    end_date = factory.LazyAttribute(
        lambda x: faker.date_between(start_date="today", end_date="+30d")
    )
    start_time = factory.LazyAttribute(lambda x: faker.time_object())
    end_time = factory.LazyAttribute(lambda x: faker.time_object())


class BookingEventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BookingEvent

    timestamp = factory.LazyAttribute(
        lambda x: faker.date_time_this_month(before_now=True, after_now=False)
    )
    rpg_status = BookingEvent.RPGStatus.BOOKING
    room = factory.SubFactory(RoomFactory)
    night_of_stay = factory.LazyAttribute(
        lambda x: faker.date_between(start_date="today", end_date="+7d")
    )


@pytest.fixture
def booking_event():
    BookingEventFactory.create_batch(4)


@pytest.fixture
def setup_data(db):
    wellington = HotelFactory.create(name="wellington")
    sunrise = HotelFactory.create(name="sunrise")
    RoomFactory.create_batch(5, hotel=wellington)
    RoomFactory.create_batch(5, hotel=sunrise)
