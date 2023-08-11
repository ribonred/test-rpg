from .models import Hotel
from rest_framework import serializers
from core.rooms.serializers import ReadRoomSerialzier


class HotelSerializer(serializers.ModelSerializer):
    rooms = ReadRoomSerialzier(many=True)

    class Meta:
        model = Hotel
        fields = (
            "id",
            "name",
            "rooms",
            "address",
            "phone",
            "website",
        )
