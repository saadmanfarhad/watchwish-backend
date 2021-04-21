from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
import jwt, datetime
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.exceptions import AuthenticationFailed
# from rest_framework.views import APIView
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

@api_view(['POST'])
def login(request):
    emailOrUsername = request.data['email']
    password = request.data['password']

    user = CustomUser.objects.filter(Q(email=emailOrUsername) | Q(username=emailOrUsername)).first()
    # user = CustomUser.objects.filter(email=emailOrUsername).first()

    if user is None:
        raise AuthenticationFailed('User not found!')

    if not user.check_password(password):
        raise AuthenticationFailed('Incorrect password')

    payload = {
        'id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10),
        'iat': datetime.datetime.utcnow()
    }

    token = jwt.encode(payload, 'secret', algorithm='HS256')

    return JsonResponse({
        'status': True,
        'accessToken': token
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_user(request):
    try:
        token = request.META['HTTP_AUTHORIZATION']
    except KeyError:
        raise AuthenticationFailed('User not authenticated')

    try:
        accessToken = token.split()[1]
        print(accessToken)
        payload = jwt.decode(accessToken, 'secret', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('User not authenticated')
    except jwt.InvalidSignatureError:
        raise AuthenticationFailed('User not authenticated')


    user = CustomUser.objects.filter(id=payload['id']).first()
    serializer = CustomUserSerializer(user)

    return Response(serializer.data)
