from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from api.serializers import UploadSerializer, AlphaSerializer, DateRangeSerializer, SettingsSerializer
from services.data_loader import upload_single_csv, load_dow30_from_dir
from services.alpha import run_alpha_strategy
from services.date_filter import set_date_range_for_state
from services.settings import get_settings, update_settings

import os

@csrf_exempt
@api_view(['POST'])
def upload_data(request):
    serializer = UploadSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    file = serializer.validated_data['file']
    try:
        rows, columns = upload_single_csv(file)
        return Response({'message': 'Data uploaded successfully', 'rows': rows, 'columns': columns})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
def load_dow30_data(request):
    
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
    try:
        result = load_dow30_from_dir(data_dir)
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
def set_date_range(request):
    serializer = DateRangeSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        set_date_range_for_state(serializer.validated_data['start_date'],
                                 serializer.validated_data['end_date'])
        return Response({'message': 'Date range set successfully'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
def calculate_alpha(request):
    serializer = AlphaSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    alpha_formula = serializer.validated_data['alpha_formula']
    try:
        result = run_alpha_strategy(alpha_formula)
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
def update_settings_view(request):
    serializer = SettingsSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    updated = update_settings(serializer.validated_data)
    return Response({'message': 'Settings updated', 'settings': updated})

@api_view(['GET'])
def get_settings_view(request):
    return Response({'settings': get_settings()})
