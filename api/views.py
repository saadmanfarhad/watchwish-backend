from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
# from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from .models import CustomUser
from .serializers import CustomUserSerializer

# from api.models import CustomUser
# from api.serializers import CustomUserSerializer
# from rest_framework.renderers import JSONRenderer
# from rest_framework.parsers import JSONParser
# user = CustomUser(email='s@gmail.com', username='sf', password='Abcd_1234', first_name='Saadman', last_name='Farhad')
# Create your views here.
@api_view(['POST'])
def register(request):
    serializer = CustomUserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
