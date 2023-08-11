from django.db import models
from helper.models import BaseTimeStampModel
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class BookingEvent(BaseTimeStampModel):
    class RPGStatus(models.IntegerChoices):
        BOOKING = 1, _("Booking")
        CANCELLATION = 2, _("Cancellation")

    timestamp = models.DateTimeField(default=timezone.now)
    rpg_status = models.IntegerField(
        choices=RPGStatus.choices, default=RPGStatus.BOOKING
    )
    room = models.ForeignKey(
        "rooms.Room", on_delete=models.CASCADE, related_name="bookings"
    )
    night_of_stay = models.DateField()

    def __str__(self):
        return f"{self.id} - {self.timestamp} - {self.rpg_status}"

    class Meta:
        ordering = ["-timestamp"]

    @property
    def hotel_id(self) -> int:
        return self.room.hotel.pk

    @property
    def room_id(self) -> int:
        return self.room.pk
