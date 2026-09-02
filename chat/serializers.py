from rest_framework import serializers
from .models import Conversation, Message
from accounts.models import AnonUser
from accounts.serializers import PublicUserSerializer


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(read_only=True)
    sender_detail = PublicUserSerializer(source='sender', read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'sender_detail', 'text', 'file_url', 'file_name', 'file_size', 'created_at', 'is_read']
        read_only_fields = ['id', 'conversation', 'sender', 'sender_detail', 'file_url', 'file_name', 'file_size', 'created_at', 'is_read']

    def get_file_url(self, obj):
        return obj.file.url if obj.file else None


class ConversationSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(queryset=AnonUser.objects.all(), many=True, write_only=True)
    participants_detail = PublicUserSerializer(source='participants', many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'is_group', 'name', 'participants', 'participants_detail', 'invite_code', 'created_at']
        read_only_fields = ['id', 'invite_code', 'created_at']