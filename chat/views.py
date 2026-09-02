from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import parser_classes
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync



@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_message_file(request, conversation_id):
    try:
        conversation = Conversation.objects.get(id=conversation_id, participants=request.user)
    except Conversation.DoesNotExist:
        return Response({'detail': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)

    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        return Response({'detail': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

    MAX_SIZE = 50 * 1024 * 1024  # 50 MB
    if uploaded_file.size > MAX_SIZE:
        return Response({'detail': 'File too large (max 50MB)'}, status=status.HTTP_400_BAD_REQUEST)

    text = request.data.get('text', '')

    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        text=text,
        file=uploaded_file,
        file_name=uploaded_file.name,
        file_size=uploaded_file.size,
    )

    serializer = MessageSerializer(message)

    # Push to everyone connected via WebSocket, same as a text message
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'conversation_{conversation_id}',
        {
            'type': 'chat_message_event',
            'message_id': str(message.id),
            'sender_id': str(request.user.id),
            'sender_name': request.user.display_name,
            'text': message.text,
            'file_url': serializer.data['file_url'],
            'file_name': message.file_name,
            'file_size': message.file_size,
            'created_at': message.created_at.isoformat(),
        }
    )

    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_conversations(request):
    conversations = request.user.conversations.all()
    serializer = ConversationSerializer(conversations, many=True)
    return Response(serializer.data)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_conversation(request):
    serializer = ConversationSerializer(data=request.data)
    if serializer.is_valid():
        conversation = serializer.save()
        conversation.participants.add(request.user)  # always include the creator
        return Response(ConversationSerializer(conversation).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request, conversation_id):
    try:
        conversation = Conversation.objects.get(id=conversation_id, participants=request.user)
    except Conversation.DoesNotExist:
        return Response({'detail': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = MessageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(conversation=conversation, sender=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_messages(request, conversation_id):
    try:
        conversation = Conversation.objects.get(id=conversation_id, participants=request.user)
    except Conversation.DoesNotExist:
        return Response({'detail': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)

    messages = conversation.messages.all()
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_group(request):
    name = request.data.get('name', '').strip()
    if not name:
        return Response({'detail': 'Group name is required'}, status=status.HTTP_400_BAD_REQUEST)

    conversation = Conversation.objects.create(
        is_group=True,
        name=name,
        invite_code=Conversation.generate_invite_code()
    )
    conversation.participants.add(request.user)

    return Response(ConversationSerializer(conversation).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_group(request, invite_code):
    try:
        conversation = Conversation.objects.get(invite_code=invite_code, is_group=True)
    except Conversation.DoesNotExist:
        return Response({'detail': 'Invalid invite link'}, status=status.HTTP_404_NOT_FOUND)

    conversation.participants.add(request.user)
    return Response(ConversationSerializer(conversation).data)