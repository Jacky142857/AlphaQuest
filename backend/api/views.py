from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from api.serializers import UploadSerializer, MultipleUploadSerializer, AlphaSerializer, DateRangeSerializer, SettingsSerializer, YFinanceSerializer
from services.data_loader import upload_single_csv, upload_multiple_csv, load_dow30_from_dir, load_yfinance_data
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
def upload_multiple_data(request):
    """
    Upload multiple CSV files, each representing a different stock.
    """
    # Handle multiple files from FormData
    files = request.FILES.getlist('files')

    if not files:
        return Response({'error': 'No files provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        result = upload_multiple_csv(files)
        return Response(result)
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

@csrf_exempt
@api_view(['POST'])
def load_yfinance_data_view(request):
    """
    Load stock data from Yahoo Finance.

    Expected request data:
    {
        "tickers": ["AAPL", "GOOGL", "MSFT"],
        "start_date": "2023-01-01",
        "end_date": "2023-12-31"
    }
    """
    serializer = YFinanceSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    tickers = serializer.validated_data['tickers']
    start_date = serializer.validated_data['start_date'].strftime('%Y-%m-%d')
    end_date = serializer.validated_data['end_date'].strftime('%Y-%m-%d')

    try:
        result = load_yfinance_data(tickers, start_date, end_date)
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
