from rest_framework import serializers
from .models import (
    NCIssueTracking, DynamicForm, IPQCWorkInfo, IPQCAssemblyAudit, BTBFitmentChecksheet,
    AssDummyTest, IPQCDisassembleCheckList, NCIssueTracking, ESDComplianceChecklist, 
    DustCountCheck, TestingFirstArticleInspection, OperatorQualificationCheck, 
    
)
 
class WorkInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPQCWorkInfo
        fields = '__all__'
        read_only_fields = ('emp_id', 'name', 'date')
 
class FAITestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestingFirstArticleInspection
        fields = '__all__'
        read_only_fields = ('emp_id', 'name', 'date')
 
class AssemblyAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPQCAssemblyAudit
        fields = '__all__'
        read_only_fields = ('emp_id', 'name', 'date')
 
class BTBChecksheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = BTBFitmentChecksheet
        fields = '__all__'
        read_only_fields = ('emp_id', 'name', 'date')
 
class DisassembleChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPQCDisassembleCheckList
        fields = '__all__'
        read_only_fields = ('emp_id', 'name', 'date')
 
class NCIssueTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = NCIssueTracking
        fields = '__all__'
        read_only_fields = ('emp_id', 'name', 'date')
 
class ESDComplianceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ESDComplianceChecklist
        fields = '__all__'
        read_only_fields = ('emp_id', 'name', 'date')
 
class OperatorQualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperatorQualificationCheck
        fields = '__all__'
        read_only_fields = ('emp_id', 'name', 'date')
 
class DustCountChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = DustCountCheck
        fields = '__all__'
        read_only_fields = ('emp_id', 'name', 'date')
 
class DynamicFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicForm
        fields = '__all__'