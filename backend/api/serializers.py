from rest_framework import serializers
from .models import UploadHistory, EquipmentData

class EquipmentDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentData
        fields = '__all__'

class UploadHistorySerializer(serializers.ModelSerializer):
    equipment_records = EquipmentDataSerializer(many=True, read_only=True)
    
    class Meta:
        model = UploadHistory
        fields = '__all__'
