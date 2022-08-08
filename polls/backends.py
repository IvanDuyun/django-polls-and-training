from django.conf import settings
from django.contrib.auth.backends import BaseBackend, ModelBackend, RemoteUserBackend
from django.contrib.auth.models import User
import jwt


class UserProfileBackend(BaseBackend):
    def authenticate(self, request, **kwargs):
        token = request.headers.get('Authorization')
        if token is None:
            print('No token')
            return None
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except:
            msg = 'Invalid authentication. Could not decode token.'
            print(msg)
            return None
        try:
            user = User.objects.get(pk=payload['id'])
        except:
            msg = 'No user matching this token was found.'
            print(msg)
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
