from django.urls import path
from . import views

urlpatterns = [
    path('conversations/', views.create_conversation, name='create-conversation'),
    path('conversations/list/', views.list_conversations, name='list-conversations'),
    path('conversations/<uuid:conversation_id>/messages/', views.send_message, name='send-message'),
    path('conversations/<uuid:conversation_id>/messages/list/', views.list_messages, name='list-messages'),
    path('conversations/<uuid:conversation_id>/messages/upload/', views.upload_message_file, name='upload-message-file'),
    path('groups/', views.create_group, name='create-group'),
    path('groups/join/<str:invite_code>/', views.join_group, name='join-group'),
]