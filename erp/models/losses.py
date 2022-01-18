# noqa
from django.db import models

from erp.models.articles import Article
from erp.models.base import BaseOperationModel, SSBaseModel


class Loss(BaseOperationModel):
    total = models.DecimalField(max_digits=10, decimal_places=2)


class LossDetail(SSBaseModel):
    loss = models.ForeignKey(Loss, on_delete=models.CASCADE)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    article = models.ForeignKey(Article, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=1)
