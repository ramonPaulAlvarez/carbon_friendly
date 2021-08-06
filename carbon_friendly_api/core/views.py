import json
import logging

import pandas as pd
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from core.serializers import EmailSerializer
from core.utils import get_latest_metrics, Datasets

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
    context = {}
    try:
        context["metrics"] = get_latest_metrics()
    except Exception as e:
        logger.error(f"Metrics error: {e}")

    return render(request, "docs.html", context=context)


def error_404(request, exception):
    """Render the 404 page."""
    context = {}
    try:
        context["metrics"] = get_latest_metrics()
    except Exception as e:
        logger.error(f"Metrics error: {e}")

    return render(request, "404.html", context=context, status=status.HTTP_404_NOT_FOUND)


def error_500(request, exception):
    """Render the 500 page."""
    context = {}
    try:
        context["metrics"] = get_latest_metrics()
    except Exception as e:
        logger.error(f"Metrics error: {e}")

    return render(request, "500.html", context=context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def index(request):
    """Render the index page."""
    context = {}
    try:
        context["metrics"] = get_latest_metrics()
    except Exception as e:
        logger.error(f"Metrics error: {e}")

    return render(request, "index.html", context=context)


class MetricViewMixin(APIView):
    """Provide base functionality to metric endpoints."""
    metric_method = None

    def filter_dataset(ds: pd.Series, query_params: dict = {}) -> pd.Series:
        """Filters the provided dataset."""
        valid_filters = (
            "created_at__gt",
            "created_at__gte",
            "created_at__lt",
            "created_at__lte",
        )

        for key, value in query_params.items():
            # Skip unsupported query params
            if key not in valid_filters:
                continue

            # Filter support for created_at
            logger.debug(f"Filtering dataset by {key} with value {value}")
            if key == "created_at__gt":
                ds = ds[ds["created_at"] > value]
            elif key == "created_at__gte":
                ds = ds[ds["created_at"] >= value]
            elif key == "created_at__lt":
                ds = ds[ds["created_at"] < value]
            elif key == "created_at__lte":
                ds = ds[ds["created_at"] <= value]

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
            # Order by descending created_at
            ds.sort_values(by=['created_at'], inplace=True, ascending=False)

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


class MethaneView(MetricViewMixin):
    """Provide the CH4 Series."""
    metric_method = Datasets.methane


class CarbonDioxideView(MetricViewMixin):
    """Provide the CO2 Series."""
    metric_method = Datasets.carbon_dioxide


class NitrousOxideView(MetricViewMixin):
    """Provide the N2O Series."""
    metric_method = Datasets.nitrous_oxide


class TemperatureChangeView(MetricViewMixin):
    """Provide the Temperature Change Series."""
    metric_method = Datasets.temperature_change
