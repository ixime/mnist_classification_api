from rest_framework import serializers

from core.models import Label


class LabelSerializer(serializers.ModelSerializer):
    """Serializer for label objects"""

    class Meta:
        model = Label
        fields = ('id', 'name')
        read_only_fields = ('id',)
