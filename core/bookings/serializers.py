from rest_framework import serializers, exceptions
from django.db import transaction
from core.rooms.models import Room
from .models import BookingEvent


class BookEventsSerializer(serializers.ModelSerializer):
    room_id = serializers.CharField(required=True)
    hotel_id = serializers.IntegerField(required=True)

    class Meta:
        model = BookingEvent
        fields = (
            "room_id",
            "hotel_id",
            "rpg_status",
            "night_of_stay",
            "id",
            "timestamp",
        )
        extra_kwargs = {
            "id": {"read_only": True},
            "timestamp": {"read_only": True},
        }

    def validate(self, attrs):
        room_id = attrs.pop("room_id")
        hotel_id = attrs.pop("hotel_id")
        try:
            room: Room = Room.objects.select_related("hotel").get(
                id=room_id, hotel__id=hotel_id
            )
        except Room.DoesNotExist:
            raise exceptions.ParseError(detail="room does not belong to this hotel")
        stayed_night = attrs["night_of_stay"]
        room_request_status = attrs["rpg_status"]
        match room_request_status:
            case 1:
                if room.is_booked(stayed_night) and attrs["rpg_status"] == 1:
                    raise exceptions.ParseError(
                        detail=f"room is already booked for date {stayed_night}"
                    )
            case 2:
                if room.is_free_or_canceled(stayed_night):
                    raise exceptions.ParseError(detail="cannot cancel event")
        attrs["room"] = room
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            event = BookingEvent.objects.create(**validated_data)
        return event
