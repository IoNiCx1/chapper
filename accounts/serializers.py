from rest_framework import serializers
from .models import AnonUser


class AnonUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnonUser
        fields  = ['id','auth_token','display_name','created_at']

class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnonUser
        fields = ['id', 'display_name']