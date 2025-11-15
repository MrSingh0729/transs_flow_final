from rest_framework import serializers
from .models import WorkInfo, FAITest, AssemblyAudit

class WorkInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkInfo
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class FAITestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAITest
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class AssemblyAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssemblyAudit
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')