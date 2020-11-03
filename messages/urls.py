"""Messages urls."""

#Django
from django.urls import path, include

# SourceStock - messages
from .views import TimesUpView


urlpatterns = [

    path('times_up', TimesUpView.as_view(), name='times_up'),

]