# noqa
from django.db import models

from erp.models.base import BasePersonModel


class Client(BasePersonModel):
    dni = models.PositiveIntegerField(null=True,
        help_text="Personal identification number")


class Provider(BasePersonModel):
    pass
