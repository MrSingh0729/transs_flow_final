from django.urls import path
from . import views
 
 
urlpatterns = [
    # Home and AJAX URLs
    path('', views.home_view, name='ipqc_home'),
    path('ajax/get-models/', views.ajax_get_models, name='ajax_get_models'),
    path('ajax/get-lines/', views.ajax_get_lines, name='ajax_get_lines'),
    path('ajax/get-groups/', views.ajax_get_groups, name='ajax_get_groups'),
    
    # Work Info URLs
    path('work-info/', views.work_info_view, name='ipqc_work_info'),
    path('work-info/list/', views.work_info_list, name='work_info_list'),
    path('work-info/<int:work_info_id>/forms/', views.forms_selection_view, name='forms_selection'),
    path('work-info/detail/<int:work_info_id>/', views.work_info_detail, name='work_info_detail'),
    path('work-info/success/', views.work_info_success, name='ipqc_work_info_success'),
    path('info_dash/', views.info_dash, name='info_dash'),
    
    # Dynamic Form URLs
    path('dynamic-form/create/', views.create_dynamic_form, name='create_dynamic_form'),
    path('dynamic-form/<int:form_id>/', views.fill_dynamic_form, name='dynamic_form'),
    path('dynamic-form/<int:form_id>/dashboard/', views.dynamic_form_dashboard, name='dynamic_form_dashboard'),
    path('dynamic-form/success/', views.dynamic_form_success, name='dynamic_form_success'),
    
    # ESD Compliance Checklist URLs
    path('esd-compliance-checklist/', views.ESDComplianceCheckListView.as_view(), name='esd_compliance_checklist_list'),
    path('esd-compliance-checklist/add/', views.ESDComplianceChecklistCreateView.as_view(), name='esd_compliance_checklist_add'),
    path('esd-compliance-checklist/details/<int:pk>/', views.esd_compliance_checklist_details, name='esd_compliance_checklist_details'),
    path('esd-compliance/success/', views.esd_success, name='esd_success'),
    
    # Disassemble Checklist URLs
    path('disassemble/add/', views.IPQCDisassembleCheckListCreateView.as_view(), name='ipqc_disassemble_add'),
    path('disassemble/', views.IPQCDisassembleCheckListView.as_view(), name='ipqc_disassemble_list'),
    path('disassemble/details/<int:pk>/', views.IPQCDisassembleDetailView.as_view(), name='ipqc_disassemble_detail'),
    path('disassemble/success/', views.disassemble_success, name='disassemble_success'),
    
    # Testing FAI management URLs
    path('testing/fai/list/', views.TestingFirstArticleInspectionListView.as_view(), name='testing_fai_list'),
    path('testing/fai/create/', views.TestingFirstArticleInspectionCreateView.as_view(), name='testing_fai_create'),
    path('testing/fai/<int:pk>/', views.TestingFirstArticleInspectionDetailView.as_view(), name='testing_fai_detail'),
    path('testing/fai/<int:pk>/download/<str:evidence_type>/', views.download_testing_fai_evidence, name='testing_download_fai_evidence'),
    path('testing/fai/public/update/<uuid:public_token>/', views.testing_fai_public_qe_update_view, name='testing_fai_public_update'),
    path('testing/fai/details/<int:pk>/', views.TestingFAIDetailsJsonView.as_view(), name='testing_fai_details_json'),
    path('testing/fai/success/', views.fai_success, name='fai_success'),
    
    # Operator Qualification Check URLs
    path('operator-qualification/create/', views.OperatorQualificationCheckCreateView.as_view(), name='operator_qualification_create'), 
    path('operator-qualification/list/', views.OperatorQualificationCheckListView.as_view(), name='operator_qualification_list'),
    path('operator-qualification/details/<int:pk>/', views.operator_qualification_detail, name='operator_qualification_detail'),
    path('operator-qualification/success/', views.operator_qualification_success, name='operator_qualification_success'),
 
    # Assembly Audit URLs
    path('assembly-audit/create/', views.IPQCAssemblyAuditCreateView.as_view(), name='ipqc_assembly_audit_create'),
    path('assembly-audit/list/', views.IPQCAssemblyAuditListView.as_view(), name='ipqc_audit_list'),
    path('assembly-audit/<int:pk>/edit/', views.IPQCAssemblyAuditUpdateView.as_view(), name='ipqc_assembly_audit_update'),
    path('assembly-audit/<int:pk>/delete/', views.IPQCAssemblyAuditDeleteView.as_view(), name='ipqc_assembly_audit_delete'),
    path('assembly-audit/success/', views.audit_success, name='audit_success'),
    
    # BTB Fitment Checksheet URLs
    path('btb-checksheet/create/', views.BTBFitmentChecksheetCreateView.as_view(), name='btb_checksheet_create'),
    path('btb-checksheet/list/', views.BTBFitmentChecksheetListView.as_view(), name='btb_checksheet_list'),
    path('btb/checksheet/<int:pk>/', views.BTBFitmentChecksheetDetailView.as_view(), name='btb_checksheet_detail'),
    path('btb-checksheet/success/', views.btb_checksheet_success, name='btb_checksheet_success'),
    
    # Dummy Test URLs
    path('ass-dummy-test/create/', views.AssyDummyTestCreate.as_view(), name='ass_dummy_test_create'),
    path('ass-dummy-test/list/', views.AssDummyTestListView.as_view(), name='ass_dummy_test_list'),
    path('ass-dummy-test/success/', views.ass_dummy_test_success, name='ass_dummy_test_success'),
    
    # NC Issue Tracking URLs
    path('nc-issue-tracking/', views.NCIssueTrackingListView.as_view(), name='nc_issue_tracking_list'),
    path('nc-issue-tracking/create/', views.NCIssueTrackingCreateView.as_view(), name='nc_issue_tracking_create'),
    path('nc-issue/success/', views.nc_issue_success, name='nc_issue_success'),
    
    # Dust Count URLs
    path('dust-count/add/', views.DustCountCreateView.as_view(), name='dust_count_checklist_add'),
    path('dust-count/list/', views.DustCountListView.as_view(), name='dust_count_checklist_list'),
    path('dust-count/success/', views.dust_count_success, name='dust_count_success'),
    
    # Bitable Webhook URL
    path('bitable/webhook/', views.lark_bitable_webhook, name='lark_bitable_webhook'),
    
    # PWA API Endpoints
    path('api/submit-offline-data/', views.api_submit_offline_data, name='api_submit_offline_data'),
    path('api/get-form-data/', views.api_get_form_data, name='api_get_form_data'),
    
    # PWA Service Worker Registration
    path('pwa/register-sw/', views.register_service_worker, name='register_service_worker'),
]