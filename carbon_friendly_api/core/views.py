import json

from carbon_friendly_api import settings
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.exceptions import ValidationError

from core.serializers import EmailSerializer


def index(request):
    """Render Landing Page"""
    return render(request, "index.html")


@csrf_exempt
def contact(request):
    """Process a contact request"""
    # Service is disabled
    if not settings.EMAIL_HOST:
        return HttpResponse(json.dumps({"error": "SMTP service not yet configured"}), content_type="application/json")

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
