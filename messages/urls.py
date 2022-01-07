"""Messages urls."""
from django.urls import path, include

from .views import TimesUpView


urlpatterns = [
    path('times_up', TimesUpView.as_view(), name='times_up'),
]
