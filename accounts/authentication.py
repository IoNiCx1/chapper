from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import AnonUser


class DeviceTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]

        try:
            user = AnonUser.objects.get(auth_token=token)
        except AnonUser.DoesNotExist:
            raise AuthenticationFailed('Invalid device token')

        return (user, None)