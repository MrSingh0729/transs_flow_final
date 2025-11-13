from django.urls import path, include
from . import views
from . import views_api
from rest_framework.routers import DefaultRouter

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'workinfo', views_api.IPQCWorkInfoViewSet, basename='workinfo')
router.register(r'fai', views_api.FAITestViewSet, basename='fai')
router.register(r'audit', views_api.AssemblyAuditViewSet, basename='audit')
router.register(r'btb', views_api.BTBChecksheetViewSet, basename='btb')
router.register(r'disassemble', views_api.DisassembleChecklistViewSet, basename='disassemble')
router.register(r'nc-issue', views_api.NCIssueTrackingViewSet, basename='nc-issue')
router.register(r'esd', views_api.ESDComplianceViewSet, basename='esd')
router.register(r'operator-qual', views_api.OperatorQualificationViewSet, basename='operator-qual')
router.register(r'dust-count', views_api.DustCountChecklistViewSet, basename='dust-count')
router.register(r'dynamic-forms', views_api.DynamicFormViewSet, basename='dynamic-forms')

urlpatterns = [
    # === API ENDPOINTS ===
    path('api/', include(router.urls)),
    # path('api/auth/token/', views_api.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/auth/token/refresh/', views_api.TokenRefreshView.as_view(), name='token_refresh'),
    
    # === WEB INTERFACE ENDPOINTS ===
    # Home and AJAX URLs
    path('', views.home_view, name='ipqc_home'),
    path('ajax/get-models/', views.ajax_get_models, name='ajax_get_models'),
    path('ajax/get-lines/', views.ajax_get_lines, name='ajax_get_lines'),
    path('ajax/get-groups/', views.ajax_get_groups, name='ajax_get_groups'),
    
    # Work Info URLs
    path('work-info/', views.work_info_view, name='ipqc_work_info'),
    path('info_dash/', views.info_dash, name='info_dash'),
    
    # Dynamic Form URLs
    path('dynamic-form/create/', views.create_dynamic_form, name='create_dynamic_form'),
    path('dynamic-form/<int:form_id>/', views.fill_dynamic_form, name='dynamic_form'),
    path('dynamic-form/<int:form_id>/dashboard/', views.dynamic_form_dashboard, name='dynamic_form_dashboard'),
    
    # ESD Compliance Checklist URLs
    path('esd-compliance-checklist/', views.ESDComplianceCheckListView.as_view(), name='esd_compliance_checklist_list'),
    path('esd-compliance-checklist/add/', views.ESDComplianceChecklistCreateView.as_view(), name='esd_compliance_checklist_add'),
    path('esd-compliance-checklist/details/<int:pk>/', views.esd_compliance_checklist_details, name='esd_compliance_checklist_details'),
    
    # Disassemble Checklist URLs
    path('disassemble/add/', views.IPQCDisassembleCheckListCreateView.as_view(), name='ipqc_disassemble_add'),
    path('disassemble/', views.IPQCDisassembleCheckListView.as_view(), name='ipqc_disassemble_list'),
    path('disassemble/details/<int:pk>/', views.IPQCDisassembleDetailView.as_view(), name='ipqc_disassemble_detail'),
    
    # Testing FAI management URLs
    path('testing/fai/list/', views.TestingFirstArticleInspectionListView.as_view(), name='testing_fai_list'),
    path('testing/fai/create/', views.TestingFirstArticleInspectionCreateView.as_view(), name='testing_fai_create'),
    path('testing/fai/<int:pk>/', views.TestingFirstArticleInspectionDetailView.as_view(), name='testing_fai_detail'),
    path('testing/fai/<int:pk>/download/<str:evidence_type>/', views.download_testing_fai_evidence, name='testing_download_fai_evidence'),
    path('testing/fai/public/update/<uuid:public_token>/', views.testing_fai_public_qe_update_view, name='testing_fai_public_update'),
    path('testing/fai/details/<int:pk>/', views.TestingFAIDetailsJsonView.as_view(), name='testing_fai_details_json'),
    
    # Operator Qualification Check URLs
    path('operator-qualification/create/', views.OperatorQualificationCheckCreateView.as_view(), name='operator_qualification_create'), 
    path('operator-qualification/list/', views.OperatorQualificationCheckListView.as_view(), name='operator_qualification_list'),
    path('operator-qualification/details/<int:pk>/', views.operator_qualification_detail, name='operator_qualification_detail'),

    # Assembly Audit URLs
    path('assembly-audit/create/', views.IPQCAssemblyAuditCreateView.as_view(), name='ipqc_assembly_audit_create'),
    path('assembly-audit/list/', views.IPQCAssemblyAuditListView.as_view(), name='ipqc_audit_list'),
    path('assembly-audit/<int:pk>/edit/', views.IPQCAssemblyAuditUpdateView.as_view(), name='ipqc_assembly_audit_update'),
    path('assembly-audit/<int:pk>/delete/', views.IPQCAssemblyAuditDeleteView.as_view(), name='ipqc_assembly_audit_delete'),
    
    # BTB Checksheet URLs
    path('btb-checksheet/create/', views.BTBFitmentChecksheetCreateView.as_view(), name='btb_checksheet_create'),
    path('btb-checksheet/list/', views.BTBFitmentChecksheetListView.as_view(), name='btb_checksheet_list'),
    path('btb/checksheet/<int:pk>/', views.BTBFitmentChecksheetDetailView.as_view(), name='btb_checksheet_detail'),
    
    # Dummy Test URLs
    path('ass-dummy-test/create/', views.AssyDummyTestCreate.as_view(), name='ass_dummy_test_create'),
    path('ass-dummy-test/list/', views.AssDummyTestListView.as_view(), name='ass_dummy_test_list'),
    
    # NC Issue Tracking URLs
    path('nc-issue-tracking/', views.NCIssueTrackingListView.as_view(), name='nc_issue_tracking_list'),
    path('nc-issue-tracking/create/', views.NCIssueTrackingCreateView.as_view(), name='nc_issue_tracking_create'),
    
    # Dust Count URLs
    path('dust-count/add/', views.DustCountCreateView.as_view(), name='dust_count_checklist_add'),
    path('dust-count/list/', views.DustCountListView.as_view(), name='dust_count_checklist_list'),
    
    # Lark Bitable Webhook
    path('bitable/webhook/', views.lark_bitable_webhook, name='lark_bitable_webhook'),
]