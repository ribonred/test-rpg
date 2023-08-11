from django.db import models
from helper.models import BaseTimeStampModel
from django.utils.translation import gettext_lazy as _
from typing import TYPE_CHECKING
import datetime
from django.conf import settings
from django_extensions.db.fields import RandomCharField

if TYPE_CHECKING:
    from bookings.models import BookingEvent


class Room(BaseTimeStampModel):
    id = RandomCharField(
        length=40, unique=True, primary_key=True, editable=False, keep_default=True
    )

    class RoomTypes(models.TextChoices):
        SINGLE = "single", _("Single")
        DOUBLE = "double", _("Double")
        SUITE = "suite", _("Suite")

    class Status(models.TextChoices):
        FREE = "free", _("Free")
        OCCUPIED = "occupied", _("Occupied")

    hotel = models.ForeignKey(
        "hotels.Hotel", on_delete=models.CASCADE, related_name="rooms"
    )
    capacity = models.IntegerField()
    room_type = models.CharField(
        max_length=20, choices=RoomTypes.choices, default=RoomTypes.SINGLE
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.FREE
    )
    room_number = models.IntegerField()

    # relations
    bookings: models.QuerySet["BookingEvent"]
    availabilities: models.QuerySet["RoomAvailability"]

    def __str__(self):
        return str(self.room_number)

    class Meta:
        verbose_name = "Room"
        verbose_name_plural = "Rooms"
        ordering = ["created"]

    def is_booked(self, at_date: str | datetime.date) -> bool:
        try:
            latest_booking = (
                self.bookings.only("pk", "rpg_status")
                .filter(night_of_stay=at_date)
                .latest("created")
            )
            return latest_booking.rpg_status == 1
        except self.bookings.model.DoesNotExist:
            return False

    def is_free_or_canceled(self, at_date: str | datetime.date) -> bool:
        try:
            latest_booking = (
                self.bookings.only("pk", "rpg_status")
                .filter(night_of_stay=at_date)
                .latest("created")
            )
            return latest_booking.rpg_status == 2
        except self.bookings.model.DoesNotExist:
            return True

    def is_available(self, at_date: str | datetime.date) -> bool:
        return (
            self.availabilities.only("pk")
            .filter(start_date__lte=at_date, end_date__gte=at_date)
            .exists()
        )


class RoomAvailability(BaseTimeStampModel):
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name="availabilities"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    cit = models.TimeField(
        default=datetime.time(settings.CHECKIN_TIME, 0), verbose_name="Check In Time"
    )
    cot = models.TimeField(
        default=datetime.time(settings.CHECKOUT_TIME, 0), verbose_name="Check Out Time"
    )

    class Meta:
        verbose_name = "Room Availability"
        verbose_name_plural = "Room Availabilities"
        ordering = ["start_date"]
