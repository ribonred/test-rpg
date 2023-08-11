from django.urls import path
from .views import BookEventsView

urlpatterns = [
    path("", BookEventsView.as_view(), name="bookingevent"),
]
