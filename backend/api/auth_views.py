# backend/api/auth_views.py
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore

from api.serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    AlphaSaveSerializer
)
from services.mongodb import user_service


@csrf_exempt
@api_view(['POST'])
def register_user(request):
    """Register a new user"""
    serializer = UserRegistrationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    user, error = user_service.create_user(
        username=data['username'],
        email=data['email'],
        password=data['password']
    )

    if error:
        return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

    # Store user ID in session
    request.session['user_id'] = user['_id']
    request.session.save()

    return Response({
        'message': 'User registered successfully',
        'user': {
            'id': user['_id'],
            'username': user['username'],
            'email': user['email'],
            'alphas': user.get('alphas', [])
        }
    }, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
def login_user(request):
    """Login user"""
    serializer = UserLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    user, error = user_service.authenticate_user(
        username=data['username'],
        password=data['password']
    )

    if error:
        return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

    # Store user ID in session
    request.session['user_id'] = user['_id']
    request.session.save()

    return Response({
        'message': 'Login successful',
        'user': {
            'id': user['_id'],
            'username': user['username'],
            'email': user['email'],
            'alphas': user.get('alphas', [])
        }
    })


@csrf_exempt
@api_view(['POST'])
def logout_user(request):
    """Logout user"""
    if 'user_id' in request.session:
        request.session.flush()

    return Response({'message': 'Logout successful'})


@csrf_exempt
@api_view(['GET'])
def get_current_user(request):
    """Get current user info"""
    user_id = request.session.get('user_id')
    if not user_id:
        return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

    user, error = user_service.get_user_by_id(user_id)
    if error:
        return Response({'error': error}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'user': {
            'id': user['_id'],
            'username': user['username'],
            'email': user['email'],
            'alphas': user.get('alphas', [])
        }
    })


@csrf_exempt
@api_view(['POST'])
def save_alpha(request):
    """Save an alpha strategy for the current user"""
    user_id = request.session.get('user_id')
    if not user_id:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = AlphaSaveSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    alpha_data = serializer.validated_data
    alpha, error = user_service.add_alpha_to_user(user_id, alpha_data)

    if error:
        return Response({'error': error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        'message': 'Alpha saved successfully',
        'alpha': alpha
    }, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['DELETE'])
def delete_alpha(request, alpha_id):
    """Delete an alpha strategy"""
    user_id = request.session.get('user_id')
    if not user_id:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    success, error = user_service.delete_alpha_from_user(user_id, alpha_id)

    if error:
        return Response({'error': error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if success:
        return Response({'message': 'Alpha deleted successfully'})
    else:
        return Response({'error': 'Alpha not found'}, status=status.HTTP_404_NOT_FOUND)


@csrf_exempt
@api_view(['PUT'])
def update_alpha(request, alpha_id):
    """Update an alpha strategy"""
    user_id = request.session.get('user_id')
    if not user_id:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = AlphaSaveSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    alpha_data = serializer.validated_data
    success, error = user_service.update_alpha_for_user(user_id, alpha_id, alpha_data)

    if error:
        return Response({'error': error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if success:
        return Response({'message': 'Alpha updated successfully'})
    else:
        return Response({'error': 'Alpha not found'}, status=status.HTTP_404_NOT_FOUND)