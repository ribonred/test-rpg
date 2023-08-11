import asyncio
import datetime
import pytz
from django.core.management.base import BaseCommand
from django.core.management import call_command
from faker import Faker
from random import randint
from core.hotels.models import Hotel
from core.rooms.models import Room
from core.bookings.models import BookingEvent
import csv
from collections import defaultdict


class Command(BaseCommand):
    help = "Create random hotels and rooms"

    async def create_booking_events(self, events_data: list[dict]):
        events_to_create = []
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"creating {len(events_data)} booking events".upper()
            )
        )
        for event in events_data:
            event.pop("hotel_id")
            timestamp = datetime.datetime.strptime(
                event["timestamp"], "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=pytz.UTC)
            event = BookingEvent(
                id=event["id"],
                room_id=event["room_id"],
                rpg_status=event["rpg_status"],
                night_of_stay=event["night_of_stay"],
                timestamp=timestamp,
                created=timestamp,
                updated=timestamp,
            )
            events_to_create.append(event)
        await BookingEvent.objects.abulk_create(events_to_create)
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"{len(events_data)} booking events created".upper()
                + "." * 5
                + self.style.SUCCESS("OK".upper())
            )
        )

    async def create_rooms(
        self, hotel: Hotel, room_ids: list[str], date_create: datetime
    ):
        rooms_to_create = []
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"creating room for hotel {hotel.pk}, {len(room_ids)} room to record".upper()
            )
        )
        for room_id in room_ids:
            room_number = randint(1, 500)
            room = Room(
                pk=room_id,
                hotel=hotel,
                capacity=randint(1, 4),
                room_type=Room.RoomTypes.choices[randint(0, 2)][0],
                room_number=room_number,
                created=date_create,
                updated=date_create,
            )
            rooms_to_create.append(room)
        return await Room.objects.abulk_create(rooms_to_create)

    async def main(self, fake, date_create, hotel_room_reservations, events_data):
        bg_tasks = set()
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"please wait, creating  {len(hotel_room_reservations.keys())} hotels record".upper()
            )
        )
        for key, value in hotel_room_reservations.items():
            hotel = await Hotel.objects.acreate(
                id=key,
                name=fake.company(),
                address=fake.address(),
                phone=f"{fake.country_calling_code()}-{fake.msisdn()}",
                email=fake.company_email(),
                website=fake.url(),
                description=fake.text(),
                created=date_create,
                updated=date_create,
            )
            task = asyncio.create_task(self.create_rooms(hotel, value, date_create))
            bg_tasks.add(task)

        await asyncio.gather(*bg_tasks)

        self.stdout.write(self.style.SUCCESS("Successfully created hotels and rooms"))
        await self.create_booking_events(events_data)

    def handle(self, *args, **options):
        call_command("flush", "--noinput")
        self.stdout.write(
            self.style.MIGRATE_HEADING("flushing database".upper())
            + "." * 5
            + self.style.SUCCESS("OK".upper())
        )
        fake = Faker()
        hotel_room_reservations = defaultdict(set)
        with open("data.csv", "r") as datafile:
            reader = csv.DictReader(datafile)
            original_headers = reader.fieldnames
            subtitude_headers = [
                ("room_reservation_id", "room_id"),
                ("status", "rpg_status"),
                ("event_timestamp", "timestamp"),
            ]
            for original, new in subtitude_headers:
                original_headers[original_headers.index(original)] = new
            events_data = list(reader)
            for row in events_data:
                hotel_room_reservations[row["hotel_id"]].add(row["room_id"])
        date_create = datetime.datetime(2020, 12, 12, tzinfo=pytz.UTC)
        asyncio.run(self.main(fake, date_create, hotel_room_reservations, events_data))
