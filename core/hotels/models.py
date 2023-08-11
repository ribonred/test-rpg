from django.db import models
from django.db.models import QuerySet
from helper.models import BaseTimeStampModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.rooms.models import Room


class Hotel(BaseTimeStampModel):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    website = models.CharField(max_length=255)
    description = models.TextField()

    # Relations
    rooms: QuerySet["Room"]

    def __str__(self):
        return self.name
