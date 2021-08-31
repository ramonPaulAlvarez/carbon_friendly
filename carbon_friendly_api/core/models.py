import uuid

from django.db import models


class Resources(models.Model):
    """Model for third party resources."""

    class Meta:
        ordering = ('name',)

    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    name = models.CharField(max_length=64)
    description = models.TextField()
    url = models.CharField(max_length=256)
    group = models.CharField(max_length=64)
    subgroup = models.CharField(max_length=64)
    icon = models.CharField(max_length=64)
    tags = models.JSONField(default=list)

