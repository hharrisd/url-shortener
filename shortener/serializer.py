from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Link
from config import settings


class LinkSerializer(serializers.ModelSerializer):
    key = serializers.SlugField(
        max_length=50, min_length=4, allow_null=True, required=False,
        validators=[
            UniqueValidator(queryset=Link.objects.all(), lookup='iexact', message=f"The proposed key already exists."),
        ]
    )
    shortened_url = serializers.SerializerMethodField()
    created_by = serializers.ReadOnlyField(source='created_by.username', default=serializers.CurrentUserDefault())

    class Meta:
        model = Link
        fields = ('url', 'key', 'shortened_url', 'created_by')

    def get_shortened_url(self, object):
        return f"{settings.BASE_DOMAIN}/{object.key}"


class LinkStatSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'key': instance.key,
            'target_url': instance.url,
            'created_at': instance.created_at.strftime(format="%Y-%m-%d %H:%M:%S"),
            'last_visit': instance.last_visit.strftime(format="%Y-%m-%d %H:%M:%S"),
            'clicks': instance.clicks
        }
