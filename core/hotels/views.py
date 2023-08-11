from rest_framework.generics import ListAPIView

from core.hotels.serializers import HotelSerializer
from .models import Hotel


class HotelsViews(ListAPIView):
    http_method_names = ["get"]
    serializer_class = HotelSerializer
    queryset = Hotel.objects.all()
