from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from django.utils import timezone
from .models import (
    NCIssueTracking, DynamicForm, IPQCWorkInfo, IPQCAssemblyAudit, BTBFitmentChecksheet,
    AssDummyTest, IPQCDisassembleCheckList, NCIssueTracking, ESDComplianceChecklist, 
    DustCountCheck, TestingFirstArticleInspection, OperatorQualificationCheck, 
    
)
from .serializers import (
    WorkInfoSerializer, FAITestSerializer, AssemblyAuditSerializer,
    BTBChecksheetSerializer, DisassembleChecklistSerializer,
    NCIssueTrackingSerializer, ESDComplianceSerializer,
    OperatorQualificationSerializer, DustCountChecklistSerializer,
    DynamicFormSerializer
)
from datetime import timedelta
 
class IPQCWorkInfoViewSet(viewsets.ModelViewSet):
    queryset = IPQCWorkInfo.objects.all()
    serializer_class = WorkInfoSerializer
    permission_classes = [IsAuthenticated]
 
    def perform_create(self, serializer):
        serializer.save(
            emp_id=self.request.user.username,
            name=self.request.user.get_full_name(),
            date=timezone.now().date()
        )
 
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        today = timezone.now().date()
        user = request.user
        
        # Get today's records
        today_records = IPQCWorkInfo.objects.filter(
            emp_id=user.username,
            date=today
        ).count()
        
        # Get week records
        week_start = today - timedelta(days=today.weekday())
        week_records = IPQCWorkInfo.objects.filter(
            emp_id=user.username,
            date__gte=week_start,
            date__lte=today
        ).count()
        
        # Get total records
        total_records = IPQCWorkInfo.objects.filter(emp_id=user.username).count()
        
        return Response({
            'today_records': today_records,
            'week_records': week_records,
            'total_records': total_records
        })
 
class FAITestViewSet(viewsets.ModelViewSet):
    queryset = TestingFirstArticleInspection.objects.all()
    serializer_class = FAITestSerializer
    permission_classes = [IsAuthenticated]
 
    def perform_create(self, serializer):
        serializer.save(
            emp_id=self.request.user.username,
            name=self.request.user.get_full_name(),
            date=timezone.now().date()
        )
 
class AssemblyAuditViewSet(viewsets.ModelViewSet):
    queryset = IPQCAssemblyAudit.objects.all()
    serializer_class = AssemblyAuditSerializer
    permission_classes = [IsAuthenticated]
 
    def perform_create(self, serializer):
        serializer.save(
            emp_id=self.request.user.username,
            name=self.request.user.get_full_name(),
            date=timezone.now().date()
        )
 
class BTBChecksheetViewSet(viewsets.ModelViewSet):
    queryset = BTBFitmentChecksheet.objects.all()
    serializer_class = BTBChecksheetSerializer
    permission_classes = [IsAuthenticated]
 
    def perform_create(self, serializer):
        serializer.save(
            emp_id=self.request.user.username,
            name=self.request.user.get_full_name(),
            date=timezone.now().date()
        )
 
class DisassembleChecklistViewSet(viewsets.ModelViewSet):
    queryset = IPQCDisassembleCheckList.objects.all()
    serializer_class = DisassembleChecklistSerializer
    permission_classes = [IsAuthenticated]
 
    def perform_create(self, serializer):
        serializer.save(
            emp_id=self.request.user.username,
            name=self.request.user.get_full_name(),
            date=timezone.now().date()
        )
 
class NCIssueTrackingViewSet(viewsets.ModelViewSet):
    queryset = NCIssueTracking.objects.all()
    serializer_class = NCIssueTrackingSerializer
    permission_classes = [IsAuthenticated]
 
    def perform_create(self, serializer):
        serializer.save(
            emp_id=self.request.user.username,
            name=self.request.user.get_full_name(),
            date=timezone.now().date()
        )
 
class ESDComplianceViewSet(viewsets.ModelViewSet):
    queryset = ESDComplianceChecklist.objects.all()
    serializer_class = ESDComplianceSerializer
    permission_classes = [IsAuthenticated]
 
    def perform_create(self, serializer):
        serializer.save(
            emp_id=self.request.user.username,
            name=self.request.user.get_full_name(),
            date=timezone.now().date()
        )
 
class OperatorQualificationViewSet(viewsets.ModelViewSet):
    queryset = OperatorQualificationCheck.objects.all()
    serializer_class = OperatorQualificationSerializer
    permission_classes = [IsAuthenticated]
 
    def perform_create(self, serializer):
        serializer.save(
            emp_id=self.request.user.username,
            name=self.request.user.get_full_name(),
            date=timezone.now().date()
        )
 
class DustCountChecklistViewSet(viewsets.ModelViewSet):
    queryset = DustCountCheck.objects.all()
    serializer_class = DustCountChecklistSerializer
    permission_classes = [IsAuthenticated]
 
    def perform_create(self, serializer):
        serializer.save(
            emp_id=self.request.user.username,
            name=self.request.user.get_full_name(),
            date=timezone.now().date()
        )
 
class DynamicFormViewSet(viewsets.ModelViewSet):
    queryset = DynamicForm.objects.all()
    serializer_class = DynamicFormSerializer
    permission_classes = [IsAuthenticated]
 
    @action(detail=False, methods=['get'])
    def my_forms(self, request):
        user_forms = DynamicForm.objects.filter(
            created_by=request.user
        ).order_by('-created_at')
        
        page = self.paginate_queryset(user_forms)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(user_forms, many=True)
        return Response(serializer.data)