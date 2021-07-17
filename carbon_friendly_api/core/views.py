import json

from carbon_friendly_api import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


def index(request):
    """Render Landing Page"""
    return render(request, "index.html")


@csrf_exempt
def contact(request):
    """Process a contact request"""
    email = request.POST.get('email', None)
    subject = request.POST.get('subject', None)
    message = request.POST.get('message', None)

    if email and subject and message:
        # Send E-Mail
        if settings.EMAIL_HOST:
            send_mail(
                f'Carbon Friendly: {subject}',
                message + "\n\n" + email,
                email,
                [email for _, email in settings.ADMINS],
                fail_silently=not(settings.DEBUG),
            )
            return HttpResponse(json.dumps({"success": "Message sent!"}), content_type="application/json")
        # E-Mail Disabled
        else:
            return HttpResponse(json.dumps({"error": "SMTP service not yet configured"}), content_type="application/json")
        
    return HttpResponse(json.dumps({"error": "email, subject, and message are required fields"}), content_type="application/json")
