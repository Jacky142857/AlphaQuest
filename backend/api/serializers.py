from rest_framework import serializers

class UploadSerializer(serializers.Serializer):
    file = serializers.FileField()

class AlphaSerializer(serializers.Serializer):
    alpha_formula = serializers.CharField()

class DateRangeSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()

class SettingsSerializer(serializers.Serializer):
    neutralization = serializers.CharField(required=False)
    decay = serializers.IntegerField(required=False)
    truncation = serializers.FloatField(required=False)
    # add others as needed
