from django.db import models

from lib.md5 import uuid_md5


class SSBaseModel(models.Model):
    STATUS_WAITING = 'w'
    STATUS_CANCELED = 'c'
    STATUS_FINISHED = 'n'

    STATUS = (
        (STATUS_WAITING, 'Waiting'),
        (STATUS_CANCELED, 'Canceled'),
        (STATUS_FINISHED, 'Finished'),
    )

    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=32, unique=True, default=uuid_md5)
    status = models.CharField(max_length=1, default=STATUS_WAITING,
        choices=STATUS)

    class Meta:
        abstract = True
