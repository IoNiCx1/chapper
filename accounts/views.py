from django.shortcuts import render

# Create your views here.

from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import AnonUser
from .serializers import AnonUserSerializer

@api_view(['POST'])
def register_device(request):
    user = AnonUser.objects.create(auth_token=AnonUser.generate_token())
    serializer = AnonUserSerializer(user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    serializer = AnonUserSerializer(request.user)
    return Response(serializer.data)

from rest_framework.parsers import JSONParser

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    name = request.data.get('display_name', '').strip()
    if name:
        request.user.display_name = name
        request.user.save()
    serializer = AnonUserSerializer(request.user)
    return Response(serializer.data)