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

# User Authentication Serializers
class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6)
    confirm_password = serializers.CharField(min_length=6)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField()

class AlphaSaveSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    formula = serializers.CharField()
    settings = serializers.DictField(required=False)
    dataSource = serializers.DictField(required=False)
    dateRange = serializers.DictField(required=False)
    returns = serializers.DictField(required=False)
    metrics = serializers.DictField(required=False)
