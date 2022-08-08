from django.conf import settings
from django.contrib.auth.backends import BaseBackend, ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
import jwt
from polls.models import UserProfile


class UserProfileBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        print('balaboba')
        token = request.headers.get('Authorization')
        print(token)

        if token is None:
            print('No token')
            return super().authenticate(self, username, password)

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
        if not user.is_active:
            msg = 'This user has been deactivated.'
            print(msg)

        print(user)
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
