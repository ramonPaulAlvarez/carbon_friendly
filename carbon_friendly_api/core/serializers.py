from rest_framework import serializers


class EmailSerializer(serializers.Serializer):
    """Serializer for e-mails."""
    from_email = serializers.EmailField(required=True)
    subject = serializers.CharField(required=True)
    message = serializers.CharField(required=True)
