from .models import Room
from rest_framework import serializers


class ReadRoomSerialzier(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ("id", "room_number")
