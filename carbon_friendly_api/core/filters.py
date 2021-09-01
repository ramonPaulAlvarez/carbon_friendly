from django_filters import rest_framework as filters
from django.db import models


class JSONFilterSet(filters.FilterSet):
    """Custom filter for JSONFields."""

    class Meta:
        filter_overrides = {
            models.JSONField: {
                'filter_class': filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
        }


class JSONFilterBackend(filters.DjangoFilterBackend):
    """Custom filter backend including support for JSONFields."""

    default_filter_set = JSONFilterSet
