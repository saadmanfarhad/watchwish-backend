import base64
import json
import jwt, datetime
import requests
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import AuthenticationFailed
from .models import CustomUser, Watchlist, Review
from .serializers import CustomUserSerializer, WatchlistSerializer, ReviewSerializer
from django.conf import settings

# Create your views here.
@api_view(['GET'])
def welcome(request):
    return JsonResponse({'message': 'Welcome to WatchWish API'})

@api_view(['POST'])
def register(request):
    if len(request.data['username']) == 0:
        return JsonResponse({'username': 'Username cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)

    if len(request.data['password']) == 0:
        return JsonResponse({'password': 'Password cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = CustomUserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse({'status': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
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

    token = jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')

    return JsonResponse({
        'status': True,
        'accessToken': token
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
def login_social(request):
    if request.data['provider'] == 'google':
        email = request.data['email']
        user = CustomUser.objects.filter(email=email).first()

        if user is None:
            accessToken = request.data['access_token']
            parts = accessToken.split(".")
            if len(parts) != 3:
                raise Exception("Incorrect id token format")

            payload = parts[1]
            padded = payload + '=' * (4 - len(payload) % 4)
            decoded = base64.b64decode(padded)
            decoded_json = json.loads(decoded)

            if decoded_json['email'] != email:
                raise AuthenticationFailed('Unauthorized')

            new_user = {
                'email': email,
                'first_name': request.data['first_name'],
                'last_name': request.data['last_name'],
                'avatar': request.data['avatar']
            }
            serializer = CustomUserSerializer(data=new_user)
            if serializer.is_valid():
                user = serializer.save()

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')

        return JsonResponse({
            'status': True,
            'accessToken': token
        }, status=status.HTTP_200_OK)

    if request.data['provider'] == 'facebook':
        response = requests.get('https://graph.facebook.com/app/?access_token=' + request.data['access_token'])
        facebook_app_details = response.json()

        if facebook_app_details['id'] != settings.FACEBOOK_APP_ID:
            raise AuthenticationFailed('Unauthorized')

        email = request.data['email']

        user = CustomUser.objects.filter(email=email).first()

        if user is None:
            new_user = {
                'email': email,
                'first_name': request.data['first_name'],
                'last_name': request.data['last_name'],
                'avatar': request.data['avatar']
            }
            serializer = CustomUserSerializer(data=new_user)
            if serializer.is_valid():
                user = serializer.save()

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')

        return JsonResponse({
            'status': True,
            'accessToken': token
        }, status=status.HTTP_200_OK)


    raise AuthenticationFailed('Unauthorized')

@api_view(['GET'])
def user(request):
    try:
        token = request.META['HTTP_AUTHORIZATION']
    except KeyError:
        raise AuthenticationFailed('User not authenticated')

    try:
        accessToken = token.split()[1]
        payload = jwt.decode(accessToken, settings.JWT_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('User not authenticated')
    except jwt.InvalidSignatureError:
        raise AuthenticationFailed('User not authenticated')

    user = CustomUser.objects.filter(id=payload['id']).first()
    serializer = CustomUserSerializer(user)

    return Response(serializer.data)

@api_view(['GET'])
def media_status(request, user_id, media_id):
    try:
        token = request.META['HTTP_AUTHORIZATION']
    except KeyError:
        raise AuthenticationFailed('User not authenticated')

    try:
        accessToken = token.split()[1]
        payload = jwt.decode(accessToken, settings.JWT_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('User not authenticated')
    except jwt.InvalidSignatureError:
        raise AuthenticationFailed('User not authenticated')

    watched = Watchlist.objects.filter(Q(user_id=user_id) & Q(media_id=media_id)).first()
    serializer = WatchlistSerializer(watched)

    return JsonResponse({'status': True, 'data': serializer.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_watchlist(request, user_id):
    paginator = PageNumberPagination()
    paginator.page_size = 2

    try:
        token = request.META['HTTP_AUTHORIZATION']
    except KeyError:
        raise AuthenticationFailed('User not authenticated')

    try:
        accessToken = token.split()[1]
        payload = jwt.decode(accessToken, settings.JWT_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('User not authenticated')
    except jwt.InvalidSignatureError:
        raise AuthenticationFailed('User not authenticated')

    watchlist = Watchlist.objects.filter(Q(user_id=user_id) & Q(watched=False))
    result_page = paginator.paginate_queryset(watchlist, request)
    serializer = WatchlistSerializer(result_page, many=True)

    return paginator.get_paginated_response(serializer.data)
    # return JsonResponse({'status': True, 'data': paginator.get_paginated_response(serializer.data)}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_watchedlist(request, user_id):
    paginator = PageNumberPagination()

    try:
        token = request.META['HTTP_AUTHORIZATION']
    except KeyError:
        raise AuthenticationFailed('User not authenticated')

    try:
        accessToken = token.split()[1]
        payload = jwt.decode(accessToken, settings.JWT_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('User not authenticated')
    except jwt.InvalidSignatureError:
        raise AuthenticationFailed('User not authenticated')

    watchedlist = Watchlist.objects.filter(Q(user_id=user_id) & Q(watched=True))
    result_page = paginator.paginate_queryset(watchedlist, request)
    serializer = WatchlistSerializer(result_page, many=True)

    return paginator.get_paginated_response(serializer.data)
    # return JsonResponse({'status': True, 'data': json.loads(results)}, status=status.HTTP_200_OK)

@api_view(['POST'])
def post_watchlist(request):
    try:
        token = request.META['HTTP_AUTHORIZATION']
    except KeyError:
        raise AuthenticationFailed('User not authenticated')

    try:
        accessToken = token.split()[1]
        payload = jwt.decode(accessToken, settings.JWT_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('User not authenticated')
    except jwt.InvalidSignatureError:
        raise AuthenticationFailed('User not authenticated')

    serializer = WatchlistSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse({'status': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def put_watchlist(request):
    try:
        token = request.META['HTTP_AUTHORIZATION']
    except KeyError:
        raise AuthenticationFailed('User not authenticated')

    try:
        accessToken = token.split()[1]
        payload = jwt.decode(accessToken, settings.JWT_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('User not authenticated')
    except jwt.InvalidSignatureError:
        raise AuthenticationFailed('User not authenticated')

    user_id = request.data['user']
    media_id = request.data['media_id']

    watched = Watchlist.objects.filter(Q(user_id=user_id) & Q(media_id=media_id)).first()
    # watched.watched = True
    serializer = WatchlistSerializer(watched, data={'watched': True}, partial=True)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse({'status': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_review(request, user_id, media_id):
    try:
        token = request.META['HTTP_AUTHORIZATION']
    except KeyError:
        raise AuthenticationFailed('User not authenticated')

    try:
        accessToken = token.split()[1]
        payload = jwt.decode(accessToken, settings.JWT_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('User not authenticated')
    except jwt.InvalidSignatureError:
        raise AuthenticationFailed('User not authenticated')

    review = Review.objects.filter(Q(user_id=user_id) & Q(media_id=media_id)).first()
    serializer = ReviewSerializer(review)

    return JsonResponse({'status': True, 'data': serializer.data}, status=status.HTTP_200_OK)

@api_view(['POST'])
def post_review(request):
    try:
        token = request.META['HTTP_AUTHORIZATION']
    except KeyError:
        raise AuthenticationFailed('User not authenticated')

    try:
        accessToken = token.split()[1]
        payload = jwt.decode(accessToken, settings.JWT_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('User not authenticated')
    except jwt.InvalidSignatureError:
        raise AuthenticationFailed('User not authenticated')

    print(request.data)

    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse({'status': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def put_review(request):
    try:
        token = request.META['HTTP_AUTHORIZATION']
    except KeyError:
        raise AuthenticationFailed('User not authenticated')

    try:
        accessToken = token.split()[1]
        payload = jwt.decode(accessToken, settings.JWT_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('User not authenticated')
    except jwt.InvalidSignatureError:
        raise AuthenticationFailed('User not authenticated')

    user_id = request.data['user']
    media_id = request.data['media_id']
    edited_review = request.data['review']

    review = Review.objects.filter(Q(user_id=user_id) & Q(media_id=media_id)).first()
    print(review)
    # watched.watched = True
    serializer = ReviewSerializer(review, data={'review': edited_review}, partial=True)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse({'status': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)