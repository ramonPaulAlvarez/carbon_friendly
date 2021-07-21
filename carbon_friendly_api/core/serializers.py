from rest_framework import serializers


class EmailSerializer(serializers.Serializer):
    """Serializer for e-mails."""
    from_email = serializers.EmailField()
    subject = serializers.CharField()
    message = serializers.CharField()

    class Meta:
        fields = (
            'from_email',
            'subject',
            'message',
        )
