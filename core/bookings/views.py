from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListCreateAPIView
from rest_framework.pagination import PageNumberPagination
from .models import BookingEvent
from .filters import BookingEventFilter
from core.bookings.serializers import BookEventsSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"


class BookEventsView(ListCreateAPIView):
    serializer_class = BookEventsSerializer
    queryset = BookingEvent.objects.all()
    filterset_class = BookingEventFilter
    pagination_class = StandardResultsSetPagination
    http_method_names = ["get", "post"]

    @extend_schema(filters=True)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(request=BookEventsSerializer)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
