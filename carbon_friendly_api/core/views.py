import json
import logging

from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.exceptions import ValidationError

from core.serializers import EmailSerializer
from core.utils import get_latest_metrics

logger = logging.getLogger(__name__)


def index(request):
    """Render Landing Page"""
    context = {}
    try:
        context["metrics"] = get_latest_metrics()
    except Exception as e:
        logger.error(f"Error reading metrics: {e}")

    return render(request, "index.html", context=context)


@csrf_exempt
def contact(request):
    """Process a contact request"""
    # Service is disabled
    if not settings.EMAIL_HOST:
        return HttpResponseServerError(json.dumps({"error": "SMTP service not yet configured"}), content_type="application/json")

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
