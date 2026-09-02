import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Conversation, Message
from accounts.models import AnonUser


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.group_name = f'conversation_{self.conversation_id}'

        query_string = self.scope['query_string'].decode()
        token = None
        for pair in query_string.split('&'):
            if pair.startswith('token='):
                token = pair.split('=')[1]

        self.user = await self.get_user_from_token(token)
        if self.user is None:
            await self.close()
            return

        is_participant = await self.check_participant(self.conversation_id, self.user)
        if not is_participant:
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get('type')

        if msg_type == 'chat_message':
            await self.handle_chat_message(data)

    async def handle_chat_message(self, data):
        text = data.get('text', '')
        message = await self.save_message(self.conversation_id, self.user, text)

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message_event',
                'message_id': str(message.id),
                'sender_id': str(self.user.id),
                'sender_name': self.user.display_name,
                'text': message.text,
                'file_url': None,
                'file_name': None,
                'file_size': None,
                'created_at': message.created_at.isoformat(),
            }
        )

    async def chat_message_event(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'id': event['message_id'],
            'sender': event['sender_id'],
            'sender_detail': {
                'id': event['sender_id'],
                'display_name': event['sender_name'],
            },
            'text': event.get('text', ''),
            'file_url': event.get('file_url'),
            'file_name': event.get('file_name'),
            'file_size': event.get('file_size'),
            'created_at': event['created_at'],
        }))

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            return AnonUser.objects.get(auth_token=token)
        except AnonUser.DoesNotExist:
            return None

    @database_sync_to_async
    def check_participant(self, conversation_id, user):
        return Conversation.objects.filter(id=conversation_id, participants=user).exists()

    @database_sync_to_async
    def save_message(self, conversation_id, user, text):
        conversation = Conversation.objects.get(id=conversation_id)
        return Message.objects.create(conversation=conversation, sender=user, text=text)