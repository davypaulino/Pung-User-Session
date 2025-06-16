from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.exceptions import InvalidToken
from django.contrib.auth.models import AnonymousUser, User

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken("Token did not contain a recognizable user identification.")

        user = User(id=user_id,
                    username=validated_token.get('nickname', user_id),
                    is_active=True)

        user.jwt_id = validated_token.get(api_settings.USER_ID_CLAIM)
        user.nickname = validated_token.get('nickname')
        user.role = validated_token.get('role')
        user.status = validated_token.get('status')

        return user