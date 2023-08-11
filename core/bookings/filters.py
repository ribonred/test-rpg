import django_filters
from .models import BookingEvent


class BookingEventFilter(django_filters.FilterSet):
    night_of_stay_from = django_filters.DateFilter(
        lookup_expr="gte", field_name="night_of_stay"
    )
    night_of_stay_to = django_filters.DateFilter(
        lookup_expr="lte", field_name="night_of_stay"
    )
    hotel_id = django_filters.CharFilter(field_name="room__hotel", lookup_expr="exact")
    event_from = django_filters.DateFilter(
        field_name="timestamp", lookup_expr="gte"
    )
    event_to = django_filters.DateFilter(
        field_name="timestamp", lookup_expr="lte"
    )

    class Meta:
        model = BookingEvent
        fields = ["hotel_id", "rpg_status", "room_id"]
