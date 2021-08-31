from rest_framework import serializers

from core.models import Resources
from django.conf import settings


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


class ResourceSerializer(serializers.ModelSerializer):
    """Serializer for third party resources."""
    
    class Meta:
        model = Resources
        fields = ('id', 'name', 'description', 'url', 'group', 'subgroup', 'icon', 'tags')
        read_only_fields = fields

    def to_representation(self, instance):
        """Update the represenation of the resource"""
        instance.icon = self.context.get('request').build_absolute_uri(f"{settings.STATIC_URL}icons/{instance.icon}")
        return super().to_representation(instance)
