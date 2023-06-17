from django.db import models


class TimeStampMixin(models.Model):
    """
    Mixin for ease adding created_at and updated_at to models.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
