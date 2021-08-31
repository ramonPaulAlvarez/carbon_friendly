import json
import logging

import pandas as pd
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django_filters import rest_framework as filters
from rest_framework import filters as drf_filters
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Resources
from core.serializers import EmailSerializer, ResourceSerializer
from core.utils import Datasets

logger = logging.getLogger(__name__)


@csrf_exempt
def contact(request):
    """Process a contact request."""
    # Service is disabled
    if not settings.EMAIL_HOST:
        error = json.dumps({"error": "SMTP service not yet configured"})
        return HttpResponse(error, status=status.HTTP_503_SERVICE_UNAVAILABLE, content_type="application/json")

    # Validate payload
    data = {
        "from_email": request.POST.get('from_email', None),
        "subject": request.POST.get('subject', None),
        "message": request.POST.get('message', None)
    }
    serializer = EmailSerializer(data=data)
    try:
        serializer.is_valid(raise_exception=True)
    except ValidationError as e:
        return HttpResponse(json.dumps(e.detail), status=status.HTTP_400_BAD_REQUEST, content_type="application/json")

    # Send message
    send_mail(
        f'Carbon Friendly: {serializer.data.get("subject")}',
        serializer.data.get('message') + "\n\n" +
        serializer.data.get('from_email'),
        serializer.data.get('from_email'),
        [email for _, email in settings.ADMINS],
        fail_silently=not(settings.DEBUG),
    )

    return HttpResponse(json.dumps({"success": "Message sent!"}), content_type="application/json")


def docs(request):
    """Render the docs page."""
    return render(request, "docs.html")


def error_404(request, exception):
    """Render the 404 page."""
    return render(request, "404.html", status=status.HTTP_404_NOT_FOUND)


def error_500(request, exception):
    """Render the 500 page."""
    return render(request, "500.html", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def index(request):
    """Render the index page."""
    context = {}

    # Gather resource items for context
    for resource in Resources.objects.order_by("group", "subgroup", "name"):
        group_pk = resource.group.lower().replace(" ", "_")
        subgroup_pk = resource.subgroup.lower().replace(" ", "_")
        if group_pk not in context:
            context[group_pk] = {}

        if subgroup_pk not in context[group_pk]:
            context[group_pk][subgroup_pk] = {"name": resource.subgroup, "resources": []}

        context[group_pk][subgroup_pk]["resources"].append(resource)

    return render(request, "index.html", context=context)


def chart(request):
    """Render the chart page."""
    return render(request, "chart.html")


class DatasetViewMixin(APIView):
    """Provide base functionality to metric endpoints."""
    metric_method = None

    def filter_dataset(ds: pd.Series, query_params: dict = {}) -> pd.Series:
        """Filters the provided dataset."""
        valid_filters = (
            "timestamp__gt",
            "timestamp__gte",
            "timestamp__lt",
            "timestamp__lte",
        )

        for key, value in query_params.items():
            # Skip unsupported query params
            if key not in valid_filters:
                continue

            # Filter support for timestamp
            logger.debug(f"Filtering dataset by {key} with value {value}")
            if key == "timestamp__gt":
                ds = ds[ds["timestamp"] > value]
            elif key == "timestamp__gte":
                ds = ds[ds["timestamp"] >= value]
            elif key == "timestamp__lt":
                ds = ds[ds["timestamp"] < value]
            elif key == "timestamp__lte":
                ds = ds[ds["timestamp"] <= value]

        return ds

    def limit_dataset(ds: pd.Series, query_params: dict = {}) -> pd.Series:
        """Limit the provided dataset."""
        value = query_params.get("limit", settings.DEFAULT_PAGE_SIZE)
        return ds[:int(value)]

    def order_dataset(ds: pd.Series, query_params: dict = {}) -> pd.Series:
        """Orders the provided dataset."""
        value = query_params.get("order_by")
        if value:
            # Skip unsupported columns
            ascending = not value.startswith("-")
            value = value.replace("-", "")

            # Order dataset
            if value in ds.columns:
                logger.debug(
                    f"Ordering dataset by {value} {'ascending' if ascending else 'descending'}")
                ds.sort_values(by=[value], inplace=True, ascending=ascending)
        else:
            # Order by descending timestamp
            ds.sort_values(by=['timestamp'], inplace=True, ascending=False)

        return ds

    @classmethod
    def get(cls, request):
        """Dynamically provide a Series."""
        if not cls.metric_method:
            return HttpResponseServerError(json.dumps({"error": "Metric not yet configured"}), content_type="application/json")

        dataset = cls.metric_method()

        try:
            metric = cls.filter_dataset(dataset, query_params=request.GET)
        except Exception as e:
            logger.error(f"Error filtering dataset: {e}")

        try:
            metric = cls.order_dataset(dataset, query_params=request.GET)
        except Exception as e:
            logger.error(f"Error ordering dataset: {e}")

        try:
            metric = cls.limit_dataset(dataset, query_params=request.GET)
        except Exception as e:
            logger.error(f"Error limiting dataset: {e}")

        records = []
        for record in metric.itertuples():
            records.append({column_name: getattr(record, column_name)
                           for column_name in metric.columns.values})

        return Response(records)
        

class CarbonDioxideView(DatasetViewMixin):
    """Provide the CO2 Series."""
    metric_method = Datasets.carbon_dioxide


class MethaneView(DatasetViewMixin):
    """Provide the CH4 Series."""
    metric_method = Datasets.methane


class NitrousOxideView(DatasetViewMixin):
    """Provide the N2O Series."""
    metric_method = Datasets.nitrous_oxide


class ResourcesView(viewsets.ReadOnlyModelViewSet):
    """Provide all third party resources."""
    queryset = Resources.objects.all()
    serializer_class = ResourceSerializer
    filter_backends = (filters.DjangoFilterBackend, drf_filters.OrderingFilter,)
    filterset_fields = ('id', 'name', 'description', 'url', 'group', 'subgroup', 'icon',)


class TemperatureChangeView(DatasetViewMixin):
    """Provide the Temperature Change Series."""
    metric_method = Datasets.temperature_change
