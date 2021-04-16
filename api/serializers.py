from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    """docstring for CustomUserSerializer."""
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'first_name', 'last_name', 'about', 'avatar',
            'date_of_birth', 'date_joined', 'date_updated'
        ]
