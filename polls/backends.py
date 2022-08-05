from django.conf import settings
from django.contrib.auth.backends import BaseBackend, ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
import jwt
from polls.models import UserProfile


class UserProfileBackend(BaseBackend):
    def authenticate(self, request, token=None):
        print('я бэкенд аутентификация, приняла токен ', token)

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
            user_profile = UserProfile.objects.get(pk=payload['id']).profile
        except:
            msg = 'No user matching this token was found.'
            print(msg)
            return None

        if not user_profile.is_active:
            msg = 'This user has been deactivated.'
            print(msg)
            return None

        print('возвращаю юзера', user_profile)
        return user_profile

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
