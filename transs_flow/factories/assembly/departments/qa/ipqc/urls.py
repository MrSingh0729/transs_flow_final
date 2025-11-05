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
    path('testing/fai/list/', views. TestingFirstArticleInspectionListView.as_view(), name='testing_fai_list'),
    path('testing/fai/create/', views. TestingFirstArticleInspectionCreateView.as_view(), name='testing_fai_create'),
    path('testing/fai/<int:pk>/', views. TestingFirstArticleInspectionDetailView.as_view(), name='testing_fai_detail'),
    path('testing/fai/<int:pk>/download/<str:evidence_type>/', views.download_testing_fai_evidence, name='testing_download_fai_evidence'),
    path('testing/fai/public/update/<uuid:public_token>/', views.testing_fai_public_qe_update_view, name='testing_fai_public_update'),
    # New URL for the JSON details view for the modal
    path('testing/fai/details/<int:pk>/', views. TestingFAIDetailsJsonView.as_view(), name='testing_fai_details_json'),
    # Operator Qualification Check URLs
    path('operator-qualification/create/', views.OperatorQualificationCheckCreateView.as_view(), name='operator_qualification_create'), 
    path('operator-qualification/list/', views.OperatorQualificationCheckListView.as_view(), name='operator_qualification_list'),
    
    # --- NEW URLS FOR LIST, UPDATE, DELETE ---
    path('assembly-audit/create/', views. IPQCAssemblyAuditCreateView.as_view(), name='ipqc_assembly_audit_create'),
    path('assembly-audit/list/', views.IPQCAssemblyAuditListView.as_view(), name='ipqc_audit_list'),
    path('assembly-audit/<int:pk>/edit/', views.IPQCAssemblyAuditUpdateView.as_view(), name='ipqc_assembly_audit_update'),
    path('assembly-audit/<int:pk>/delete/', views.IPQCAssemblyAuditDeleteView.as_view(), name='ipqc_assembly_audit_delete'),
    path('btb-checksheet/create/', views. BTBFitmentChecksheetCreateView.as_view(), name='btb_checksheet_create'),
    path('btb-checksheet/list/', views. BTBFitmentChecksheetListView.as_view(), name='btb_checksheet_list'),
    path('btb/checksheet/<int:pk>/', views.BTBFitmentChecksheetDetailView.as_view(), name='btb_checksheet_detail'),
    path('ass-dummy-test/create/', views.AssyDummyTestCreate.as_view(), name='ass_dummy_test_create'),
    path('ass-dummy-test/list/', views.AssDummyTestListView.as_view(), name='ass_dummy_test_list'),
    path('nc-issue-tracking/', views.NCIssueTrackingListView.as_view(), name='nc_issue_tracking_list'),
    path('nc-issue-tracking/create/', views.NCIssueTrackingCreateView.as_view(), name='nc_issue_tracking_create'),
    path('dust-count/add/', views.DustCountCreateView.as_view(), name='dust_count_checklist_add'),
    path('dust-count/list/', views.DustCountListView.as_view(), name='dust_count_checklist_list'),
    path('bitable/webhook/', views.lark_bitable_webhook, name='lark_bitable_webhook'),

]