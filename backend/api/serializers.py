from rest_framework import serializers

class UploadSerializer(serializers.Serializer):
    file = serializers.FileField()

class AlphaSerializer(serializers.Serializer):
    alpha_formula = serializers.CharField()

class DateRangeSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()

class SettingsSerializer(serializers.Serializer):
    neutralization = serializers.BooleanField(required=False)
    decay = serializers.IntegerField(required=False)
    truncation = serializers.FloatField(required=False)
    pasteurization = serializers.CharField(required=False)
    nanHandling = serializers.CharField(required=False)
    maxTrade = serializers.CharField(required=False)
    delay = serializers.IntegerField(required=False)
    commission = serializers.FloatField(required=False)
    bookSize = serializers.IntegerField(required=False)
    minWeight = serializers.FloatField(required=False)
    maxWeight = serializers.FloatField(required=False)
    rebalanceFreq = serializers.CharField(required=False)

class YFinanceSerializer(serializers.Serializer):
    tickers = serializers.ListField(
        child=serializers.CharField(max_length=10),
        min_length=1,
        help_text="List of stock ticker symbols (e.g., ['AAPL', 'GOOGL', 'MSFT'])"
    )
    start_date = serializers.DateField(help_text="Start date in YYYY-MM-DD format")
    end_date = serializers.DateField(help_text="End date in YYYY-MM-DD format")
