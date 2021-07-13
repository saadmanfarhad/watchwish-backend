from rest_framework import serializers
from .models import CustomUser, Watchlist, Review
from rest_framework.exceptions import APIException
from django.utils.encoding import force_text
from rest_framework import status

class CustomUserSerializer(serializers.ModelSerializer):
    """docstring for CustomUserSerializer."""
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'password', 'first_name', 'last_name', 'about', 'avatar',
            'date_of_birth', 'date_joined', 'date_updated'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        try :
            username = validated_data['username']
            try:
                if validated_data['username']:
                    uid = CustomUser.objects.filter(username=username)
                    if uid.count() > 0:
                        raise CustomValidation('Duplicate Username','username', status_code=status.HTTP_409_CONFLICT)
            except CustomUser.DoesNotExist:
                pass
        except KeyError:
            pass

        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class WatchlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watchlist
        fields = ['id', 'user', 'media_id', 'media_type', 'watched']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'user', 'media_id', 'review']

class CustomValidation(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A server error occurred.'

    def __init__(self, detail, field, status_code):
        if status_code is not None:self.status_code = status_code
        if detail is not None:
            self.detail = {field: force_text(detail)}
        else: self.detail = {'detail': force_text(self.default_detail)}
