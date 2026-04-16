from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Statue, SearchHistory


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class StatueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statue
        fields = '__all__'


class SearchHistorySerializer(serializers.ModelSerializer):
    statue_details = StatueSerializer(source='statue', read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = SearchHistory
        fields = ['id', 'statue', 'statue_details', 'image_url', 'confidence', 'created_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image_searched and request:
            return request.build_absolute_uri(obj.image_searched.url)
        return None
