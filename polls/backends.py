from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
import jwt
from polls.models import UserProfile


class UserProfileBackend(BaseBackend):

    def authenticate(self, request, **kwargs):
        user = kwargs['username']
        password = kwargs['password']

        user_profile = None
        #token = None
        print(request.headers)
        print(request.headers['Jwt'])

        token = request.headers['Jwt']

        if token is None:
            return None

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except:
            msg = 'Invalid authentication. Could not decode token.'
            print(msg)

        try:
            user_profile = UserProfile.objects.get(pk=payload['id'])
        except:
            msg = 'No user matching this token was found.'
            print(msg)

        if not user.is_active:
            msg = 'This user has been deactivated.'
            print(msg)

        return (user_profile, token)

        '''try:
            if user_profile.profile.check_password(password) is True:
                return (user_profile, token)
        except UserProfile.DoesNotExist:
            pass'''

        '''try:
            user_profile = UserProfile.objects.get(pk=profile_id)
            if user_profile.profile.check_password(password) is True:
                return user_profile.profile
        except UserProfile.DoesNotExist:
            pass'''

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
