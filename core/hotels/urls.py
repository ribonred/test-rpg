from django.urls import path
from .views import HotelsViews

urlpatterns = [
    path("", HotelsViews.as_view(), name="hotels"),
]
