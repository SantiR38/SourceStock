# noqa
from django.db import models

from lib.md5 import uuid_md5


class SSBaseModel(models.Model):
    STATUS_WAITING = 'w'
    STATUS_CANCELED = 'c'
    STATUS_FINISHED = 'f'

    STATUS = (
        (STATUS_WAITING, 'Waiting'),
        (STATUS_CANCELED, 'Canceled'),
        (STATUS_FINISHED, 'Finished'),
    )

    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=32, unique=True, default=uuid_md5)
    is_deleted = models.BooleanField(default=False)
    status = models.CharField(max_length=1, default=STATUS_FINISHED,
        choices=STATUS)

    class Meta:
        abstract = True


class BaseOperationModel(SSBaseModel):
    status = models.CharField(max_length=1, default=SSBaseModel.STATUS_WAITING,
        choices=SSBaseModel.STATUS)

    class Meta:
        abstract = True


class BasePersonModel(SSBaseModel):
    TAX_REGISTERED_PAYER = 'rp'
    TAX_SINGLE_PAYER = 'sp'
    TAX_EXEMPT = 'ex'
    TAX_NOT_REACHED = 'nr'
    TAX_FINAL_CONSUMER = 'fc'

    TAXES = (
        (TAX_REGISTERED_PAYER, 'Responsable Inscripto'),
        (TAX_SINGLE_PAYER, 'Monotributista'),
        (TAX_EXEMPT, 'IVA Excento'),
        (TAX_NOT_REACHED, 'No Alcanzado'),
        (TAX_FINAL_CONSUMER, 'Consumidor Final'),
    )

    name = models.CharField(max_length=50)
    tax_condition = models.CharField(max_length=25, default=TAX_FINAL_CONSUMER,
        choices=TAXES)
    cuit = models.CharField(max_length=15, null=True,
        help_text="Personal tax identification number")
    direction = models.CharField(max_length=50, null=True)
    phone_number = models.CharField(max_length=30, null=True)
    email = models.EmailField(null=True)

    class Meta:
        abstract = True
