from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django import forms
import json
from accounts.models import Employee
from .forms import WorkInfoForm, IPQCAssemblyAuditForm, FIELDS_WITH_REMARKS, BTBFitmentChecksheetForm, AssDummyTestForm, IPQCDisassembleCheckListForm, NCIssueTrackingForm, ESDComplianceChecklistForm, DustCountCheckForm, TestingFirstArticleInspectionForm, OperatorQualificationCheckForm
from .services import write_to_bitable, write_to_bitable_dynamic, date_to_ms
from datetime import timedelta, datetime, date
from .models import IPQCWorkInfo, DynamicForm, DynamicFormField, DynamicFormSubmission, IPQCAssemblyAudit, BTBFitmentChecksheet, AssDummyTest, IPQCDisassembleCheckList, NCIssueTracking, ESDComplianceChecklist, DustCountCheck, TestingFirstArticleInspection, OperatorQualificationCheck
import pandas as pd
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DetailView
from accounts.role_decorator import RoleRequiredMixin, role_required
from django.db.models import Q
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, Http404
from django.db import connections
from django.views.decorators.http import require_GET
from django.conf import settings
from django.http import HttpResponse
import os
from django.urls import reverse
import requests
 
# ==============================================================================
# PWA HELPER FUNCTIONS
# ==============================================================================
 
def is_mobile(request):
    """Detect if the request is from a mobile device"""
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    mobile_agents = ['android', 'iphone', 'ipod', 'ipad', 'blackberry', 'windows phone']
    return any(agent in user_agent for agent in mobile_agents)
 
def get_pwa_context(request):
    """Get PWA context for templates"""
    return {
        'is_mobile': is_mobile(request),
        'pwa_manifest_url': '/static/manifest.json',
        'service_worker_url': '/static/service-worker.js',
        'api_base_url': '/api/',
        'offline_sync_supported': False,  # Will be set in template
    }
 
# ==============================================================================
# EXISTING FUNCTION-BASED VIEWS (WITH PWA ENHANCEMENTS)
# ==============================================================================
 
# --- Fetch models dynamically from your DB ---
def ajax_get_models(request):
    q = request.GET.get('q', '').strip()
    try:
        with connections['defaultdb'].cursor() as cursor:
            cursor.execute("""
                SELECT model_name 
                FROM model_description 
                WHERE model_name LIKE %s 
                ORDER BY model_name ASC
                LIMIT 20;
            """, [f"%{q}%"])
            rows = cursor.fetchall()
        data = [{'id': r[0], 'text': r[0]} for r in rows]
    except Exception as e:
        data = []
    return JsonResponse(data, safe=False)
 
 
# --- Static list for lines (L1–L15) ---
def ajax_get_lines(request):
    q = request.GET.get('q', '').strip().upper()
    lines = [f"L{i}" for i in range(1, 16)]
    filtered = [l for l in lines if q in l]
    return JsonResponse([{'id': l, 'text': l} for l in filtered], safe=False)
 
 
# --- Static list for groups (A1–A15) ---
def ajax_get_groups(request):
    q = request.GET.get('q', '').strip().upper()
    groups = [f"A{i}" for i in range(1, 16)]
    filtered = [g for g in groups if q in g]
    return JsonResponse([{'id': g, 'text': g} for g in filtered], safe=False)
 
@login_required
@role_required(["IPQC"])
def work_info_view(request):
    emp_id = getattr(request.user, 'employee_id', None)
    full_name = getattr(request.user, 'full_name', None)
 
    # --- Safety: fallback if missing in user model ---
    if not emp_id or not full_name:
        try:
            employee = Employee.objects.get(user=request.user)
            emp_id = employee.employee_id
            full_name = employee.full_name
        except Employee.DoesNotExist:
            messages.error(request, "Employee record not found for this user.")
            return redirect('ipqc_home')
 
    today = timezone.localdate()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
 
    today_records = IPQCWorkInfo.objects.filter(date=today, emp_id=emp_id).count()
    week_records = IPQCWorkInfo.objects.filter(date__range=[start_of_week, end_of_week], emp_id=emp_id).count()
    total_records = IPQCWorkInfo.objects.filter(emp_id=emp_id).count()
    recent_records = IPQCWorkInfo.objects.filter(emp_id=emp_id).order_by('-created_at')[:5]
 
    if request.method == 'POST':
        form = WorkInfoForm(request.POST)
        if form.is_valid():
            work_info = form.save(commit=False)
 
            # Always attach employee info
            work_info.emp_id = emp_id
            work_info.name = full_name
            work_info.created_at = timezone.now()
 
            work_info.save()
 
            # PWA: Add data to context for frontend to save to IndexedDB
            context = {
                'offline_data': {
                    'type': 'workinfo',
                    'id': str(work_info.id),
                    'data': {
                        'date': str(work_info.date),
                        'shift': work_info.shift,
                        'emp_id': work_info.emp_id,
                        'name': work_info.name,
                        'section': work_info.section,
                        'line': work_info.line,
                        'group': work_info.group,
                        'model': work_info.model,
                        'color': work_info.color,
                    }
                }
            }
 
            success, message = write_to_bitable(work_info)
            if success:
                messages.success(request, 'Work info saved and synced to Lark Bitable!')
            else:
                messages.warning(request, f'Work info saved but failed to sync: {message}')
 
            return render(request, 'ipqc/success/work_info_success.html', context)
    else:
        form = WorkInfoForm()
 
    line_list = [f"L{i}" for i in range(1, 16)]
    group_list = [f"A{i}" for i in range(1, 16)]
 
    context = {
        'first_name': full_name.split()[0] if full_name else "",
        'designation': getattr(request.user, "role", ""),
        'form': form,
        'user_emp_id': emp_id,
        'user_name': full_name,
        'today_records': today_records,
        'week_records': week_records,
        'total_records': total_records,
        'recent_records': recent_records,
        'start_of_week': start_of_week,
        'end_of_week': end_of_week,
        'line_list': line_list,
        'group_list': group_list,
        **get_pwa_context(request)
    }
 
    return render(request, 'ipqc/work_info.html', context)
 
@csrf_exempt
def lark_bitable_webhook(request):
    """Webhook endpoint for Lark Bitable automation trigger"""
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid method"}, status=405)
 
    try:
        payload = json.loads(request.body.decode('utf-8'))
        fields = payload.get('fields', {})
        
        emp_id = fields.get('Emp_ID')
        model_name = fields.get('Model')
        date = fields.get('Date')
        status = fields.get('Status')
 
        if not all([emp_id, model_name, date, status]):
            return JsonResponse({"error": "Missing required fields"}, status=400)
 
        # Convert date if it's in timestamp (ms)
        if isinstance(date, int):
            date = datetime.fromtimestamp(date / 1000).date()
 
        # Update corresponding record
        updated = IPQCWorkInfo.objects.filter(emp_id=emp_id, model=model_name, date=date).update(status=status)
 
        if updated:
            return JsonResponse({"message": "Status updated successfully"})
        else:
            return JsonResponse({"error": "Record not found"}, status=404)
 
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
 
@login_required
@role_required(["IPQC"])
def home_view(request):
    user = request.user
    emp_id = getattr(user, 'employee_id', None)
 
    now = timezone.localtime()
    today_8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
    today = now.date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)
 
    # Define the time range (8 AM today → 8 AM next day)
    if now < today_8am:
        start_time = today_8am - timedelta(days=1)
        end_time = today_8am
    else:
        start_time = today_8am
        end_time = today_8am + timedelta(days=1)
 
    # Check if created_at is within current 8AM–8AM window
    has_filled = IPQCWorkInfo.objects.filter(
        emp_id=emp_id,
        created_at__gte=start_time,
        created_at__lt=end_time
    ).exists()
 
    if not has_filled:
        messages.warning(
            request,
            "⚠️ You haven't filled your Work Info for the current period (8 AM to next day 8 AM). Please fill it before proceeding."
        )
        return redirect('ipqc_work_info')
 
    is_admin = user.is_superuser or getattr(user, 'role', '').lower() == 'admin'
    
    # Set filters for non-admin users
    base_filter = {}
    if not is_admin and emp_id:
        base_filter['inspector_name'] = getattr(user, 'full_name', '') or user.username
 
    # Work Info counts
    work_info_today = IPQCWorkInfo.objects.filter(date=today, emp_id=emp_id).count()
    work_info_week = IPQCWorkInfo.objects.filter(date__range=[start_of_week, today], emp_id=emp_id).count()
    work_info_month = IPQCWorkInfo.objects.filter(date__range=[start_of_month, today], emp_id=emp_id).count()
 
    # Assembly Audit counts
    audit_today = IPQCAssemblyAudit.objects.filter(date=today, emp_id=emp_id).count()
    audit_week = IPQCAssemblyAudit.objects.filter(date__range=[start_of_week, today], emp_id=emp_id).count()
    audit_month = IPQCAssemblyAudit.objects.filter(date__range=[start_of_month, today], emp_id=emp_id).count()
 
    # ESD Compliance counts
    esd_today = ESDComplianceChecklist.objects.filter(date=today, emp_id=emp_id).count()
    esd_week = ESDComplianceChecklist.objects.filter(date__range=[start_of_week, today], emp_id=emp_id).count()
    esd_month = ESDComplianceChecklist.objects.filter(date__range=[start_of_month, today], emp_id=emp_id).count()
 
    # IPQC Disassemble counts
    disassemble_today = IPQCDisassembleCheckList.objects.filter(date=today, emp_id=emp_id).count()
    disassemble_week = IPQCDisassembleCheckList.objects.filter(date__range=[start_of_week, today], emp_id=emp_id).count()
    disassemble_month = IPQCDisassembleCheckList.objects.filter(date__range=[start_of_month, today], emp_id=emp_id).count()
 
    # FAI counts
    fai_today = TestingFirstArticleInspection.objects.filter(date=today, **base_filter).count()
    fai_week = TestingFirstArticleInspection.objects.filter(date__range=[start_of_week, today], **base_filter).count()
    fai_month = TestingFirstArticleInspection.objects.filter(date__range=[start_of_month, today], **base_filter).count()
 
    recent_audits = IPQCAssemblyAudit.objects.filter(emp_id=emp_id).order_by('-created_at')[:5]
    dynamic_forms = DynamicForm.objects.all().order_by('-created_at')
 
    full_name = getattr(user, 'full_name', '') or f"{user.first_name} {user.last_name}".strip()
 
    context = {
        'Full_Name': full_name,
        'designation': getattr(user, "role", ""),
        'is_admin': is_admin,
        'dynamic_forms': dynamic_forms,
        
        # Work Info counts
        'work_info_today': work_info_today,
        'work_info_week': work_info_week,
        'work_info_month': work_info_month,
        
        # Audit counts
        'audit_today': audit_today,
        'audit_week': audit_week,
        'audit_month': audit_month,
        
        # ESD counts
        'esd_today': esd_today,
        'esd_week': esd_week,
        'esd_month': esd_month,
        
        # Disassemble counts
        'disassemble_today': disassemble_today,
        'disassemble_week': disassemble_week,
        'disassemble_month': disassemble_month,
        
        # FAI counts
        'fai_today': fai_today,
        'fai_week': fai_week,
        'fai_month': fai_month,
        
        'recent_audits': recent_audits,
        **get_pwa_context(request)
    }
 
    return render(request, 'ipqc/home.html', context)
 
@login_required
@role_required(["IPQC", "QA"])
def info_dash(request):
    emp_id = request.user.employee_id
 
    today = timezone.localdate()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
 
    today_records = IPQCWorkInfo.objects. filter(date=today, emp_id=emp_id).count()
    week_records = IPQCWorkInfo.objects. filter(
    date__range=[start_of_week, end_of_week],
    emp_id=emp_id
    ).count()
    total_records = IPQCWorkInfo.objects. filter(emp_id=emp_id).count()
    recent_records = IPQCWorkInfo.objects. filter(
    emp_id=emp_id,
    date__range=[start_of_week, end_of_week]
    ).order_by('-created_at')[:5]
 
    context = {
        'first_name': request.user.full_name.split()[0],
        'designation': request.user.role,
        'today_records': today_records,
        'week_records': week_records,
        'total_records': total_records,
        'recent_records': recent_records,
        **get_pwa_context(request)
    }
    return render(request, 'ipqc/info_dash.html', context)
 
 
@login_required
@role_required()
def fill_dynamic_form(request, form_id):
    form_obj = get_object_or_404(DynamicForm, id=form_id)
    fields = form_obj.fields. all()
 
    work_info_today = IPQCWorkInfo.objects. filter(
        emp_id=request.user.employee_id,
        date=timezone.localdate()
    ).order_by('-created_at').first()
 
    if not work_info_today:
        messages.warning(request, "Please fill your IPQC Work Info for today before submitting dynamic forms.")
        return redirect('ipqc_work_info')
 
    prefill_work_info = {
        'Emp_ID': work_info_today.emp_id,
        'Name': work_info_today.name,
        'Section': work_info_today.section,
        'Line': work_info_today.line,
        'Group': work_info_today.group,
        'Model': work_info_today.model,
        'Color': work_info_today.color,
        'Date': work_info_today.date,
        'Shift': work_info_today.shift
    }
 
    CustomForm = type('CustomForm', (forms. Form,), {})
 
    for key, value in prefill_work_info.items():
        if key == 'Date':
            CustomForm.base_fields[key] = forms. DateField(
                initial=value,
                widget=forms. DateInput(attrs={'type': 'date'}),
                required=True
            )
        else:
            CustomForm.base_fields[key] = forms. CharField(initial=value, required=True)
 
    for field in fields:
        if field.field_type == 'text':
            CustomForm.base_fields[field.label] = forms. CharField(required=field.required)
        elif field.field_type == 'number':
            CustomForm.base_fields[field.label] = forms. IntegerField(required=field.required)
        elif field.field_type == 'date':
            CustomForm.base_fields[field.label] = forms. DateField(
                widget=forms. DateInput(attrs={'type': 'date'}),
                required=field.required
            )
        elif field.field_type == 'select':
            choices = [(opt.strip(), opt.strip()) for opt in (field.options or "").split(',')]
            CustomForm.base_fields[field.label] = forms. ChoiceField(choices=choices, required=field.required)
        elif field.field_type == 'checkbox':
            CustomForm.base_fields[field.label] = forms. BooleanField(required=field.required)
 
    if request.method == 'POST':
        form = CustomForm(request. POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
 
            dynamic_data = {k: v for k, v in cleaned_data.items() if k not in prefill_work_info}
            submission = DynamicFormSubmission.objects.create(
                form=form_obj,
                submitted_by=request.user,
                data=dynamic_data
            )
 
            ipqc_data = {k: v for k, v in cleaned_data.items() if k in prefill_work_info}
            for field, value in ipqc_data.items():
                setattr(work_info_today, field.lower(), value)
            work_info_today.save()
 
            combined_data = {**ipqc_data, **dynamic_data}
            if 'Date' in combined_data and isinstance(combined_data['Date'], (datetime, date)):
                combined_data['Date'] = date_to_ms(combined_data['Date'])
 
            # PWA: Add data to context for frontend to save to IndexedDB
            context = {
                'offline_data': {
                    'type': 'dynamic_form',
                    'id': str(submission.id),
                    'form_id': form_id,
                    'data': combined_data
                }
            }
            
            success, message = write_to_bitable_dynamic(form_obj.lark_bitable_table_id, combined_data)
            messages.success(
                request,
                f"Form submitted! {message if success else 'Saved locally to MySQL.'}"
            )
            return render(request, 'ipqc/dynamic_form_success.html', context)
    else:
        form = CustomForm()
 
    return render(request, 'ipqc/dynamic_form.html', {
        'form': form,
        'form_obj': form_obj,
        'work_info_today': work_info_today,
        **get_pwa_context(request)
    })
 
 
@login_required
@role_required()
def create_dynamic_form(request):
    if request.method == "POST":
        title = request. POST.get("title").strip()
        description = request. POST.get("description")
        lark_bitable_table_id = request. POST.get("lark_bitable_table_id")
        fields_data = request. POST.get("fields_data")
 
        if DynamicForm.objects. filter(title__iexact=title).exists():
            messages.error(request, f"A form with the title '{title}' already exists.")
            return redirect('create_dynamic_form')
 
        if not fields_data:
            messages.error(request, "Please add at least one field.")
            return redirect('create_dynamic_form')
 
        try:
            fields = json.loads(fields_data)
        except:
            messages.error(request, "Invalid field data.")
            return redirect('create_dynamic_form')
 
        dynamic_form = DynamicForm.objects.create(
            title=title,
            description=description,
            lark_bitable_table_id=lark_bitable_table_id
        )
 
        for idx, field in enumerate(fields):
            DynamicFormField.objects.create(
                form=dynamic_form,
                label=field.get("label"),
                field_type=field.get("type"),
                required=field.get("required", True),
                order=idx
            )
 
        messages.success(request, "Dynamic form created successfully!")
        return redirect('ipqc_home')
 
    return render(request, "ipqc/create_dynamic_form.html", **get_pwa_context(request))
 
 
@login_required
@role_required()
def dynamic_form_dashboard(request, form_id):
    form_obj = get_object_or_404(DynamicForm, id=form_id)
    submissions = DynamicFormSubmission.objects. filter(form=form_obj)
 
    df = pd. DataFrame([s.data for s in submissions])
    df['submitted_by'] = [s.submitted_by.full_name for s in submissions]
    df['created_at'] = [s.created_at for s in submissions]
 
    total_submissions = len(df)
    latest_submission = df['created_at']. max() if  not df.empty else  None
 
    numeric_summary = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            numeric_summary[col] = {
                'mean': round(df[col].mean(), 2),
                'max': df[col]. max(),
                'min': df[col]. min(),
            }
 
    context = {
        "form_obj": form_obj,
        'total_submissions': total_submissions,
        "latest_submission": latest_submission,
        "numeric_summary": numeric_summary,
        "data_json": df.to_json(orient='records') if not df.empty else '[]',
        **get_pwa_context(request)
    }
 
    return render(request, "ipqc/dynamic_dashboard.html", context)
 
 
# ==============================================================================
# IPQC ASSEMBLY AUDIT VIEWS (NEW & UPDATED)
# ==============================================================================
 
class UserCanEditAuditMixin(UserPassesTestMixin):
    def test_func(self):
        audit = self.get_object()
        user = self.request.user
        if user.is_superuser or user.role.lower() == 'admin':
            return True
        return audit.emp_id == user.employee_id
 
class IPQCAssemblyAuditListView(RoleRequiredMixin, LoginRequiredMixin, ListView):
    allowed_roles = ["IPQC"]
    model = IPQCAssemblyAudit
    template_name = 'ipqc/audit_list.html'
    context_object_name = 'audits'
    paginate_by = 10
 
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role.lower() == 'admin':
            return IPQCAssemblyAudit.objects. all()
        else:
            return IPQCAssemblyAudit.objects. filter(emp_id=user.employee_id)
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin'] = self.request.user.is_superuser or self.request.user.role.lower() == 'admin'
        context.update(get_pwa_context(self.request))
        return context
 
class IPQCAssemblyAuditCreateView(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    allowed_roles = ["IPQC"]
    model = IPQCAssemblyAudit
    form_class = IPQCAssemblyAuditForm
    template_name = 'ipqc/ipqc_assembly_audit_form.html'
    success_url = reverse_lazy('ipqc_audit_list')
    
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        emp_id = getattr(user, 'employee_id', None)
 
        if emp_id:
            now = timezone.localtime()
            today = now.date()
            today_8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
            start_time = today_8am - timedelta(days=1) if now < today_8am else today_8am
            end_time = start_time + timedelta(days=1)
 
            has_filled = IPQCWorkInfo.objects.filter(
                emp_id=emp_id,
                created_at__range=[start_time, end_time]
            ).exists()
 
            if not has_filled:
                messages.warning(request, "⚠️ You haven't filled your Work Info for today. Please fill it before proceeding.")
                return redirect('ipqc_work_info')
 
        return super().dispatch(request, *args, **kwargs)
 
    def get_initial(self):
        initial = super().get_initial()
        emp_id = getattr(self.request.user, 'employee_id', None)
 
        initial['ipqc_sign'] = getattr(self.request.user, 'full_name', self.request.user.employee_id)
 
        if emp_id:
            try:
                latest_work_info = IPQCWorkInfo.objects. filter(emp_id=emp_id).latest('created_at')
                initial.update({
                    'date': latest_work_info.date, 'shift': latest_work_info.shift,
                    'emp_id': latest_work_info.emp_id, 'name': latest_work_info.name,
                    'section': latest_work_info.section, 'line': latest_work_info.line,
                    'group': latest_work_info.group, 'model': latest_work_info.model,
                    'color': latest_work_info.color,
                })
            except IPQCWorkInfo.DoesNotExist:
                messages.warning(self.request, "No Work Information found. Some fields may be empty.")
        
        return initial
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context['form']
        
        context['machine_fields'] = [
            form['mach_epa_check'], form['mach_screw_torque'], form['mach_sholdering_temp'], 
            form['mach_light'], form['mach_fixture_clean'], form['mach_jig_label'], 
            form['mach_teflon'], form['mach_press_params'], form['mach_glue_params'],
            form['mach_eq_move_notify'], form['mach_feeler_gauge'], form['mach_hot_cold_press'], 
            form['mach_ion_fan'], form['mach_cleanroom_eq'], form['mach_rti_check'], 
            form['mach_current_test'], form['mach_pal_qr'], form['mach_auto_screw'],
        ]
 
        context['material_fields'] = [
            form['mat_key_check'], form['mat_special_stop'], form['mat_improved_monitor'], 
            form['mat_result_check'], form['mat_battery_issue'], form['mat_ipa_check'], 
            form['mat_thermal_gel'], form['mat_verification'],
        ]
 
        context['method_fields'] = [
            form['meth_sop_seq'], form['meth_distance_sensor'], form['meth_rear_camera'], 
            form['meth_material_handling'], form['meth_guideline_doc'], form['meth_operation_doc'], 
            form['meth_defective_feedback'], form['meth_line_record'], form['meth_no_self_repair'], 
            form['meth_battery_fix'], form['meth_line_change'], form['meth_trail_run'], 
            form['meth_dummy_conduct'],
        ]
 
        context['environment_fields'] = [
            form['env_prod_monitor'], form['env_5s'],
        ]
 
        context['trc_fields'] = [
            form['trc_flow_chart'], form['fai_check'], form['defect_monitor'], 
            form['spot_check'], form['auto_screw_sample'],
        ]
        
        context.update(get_pwa_context(self.request))
        return context
 
    def form_valid(self, form):
        form.instance.emp_id = self.request.user.employee_id
        form.instance.name = self.request.user.full_name
        form.instance.remarks = self.request.POST.get('remarks', '').strip()
        
        # PWA: Add data to context for frontend to save to IndexedDB
        context = {
            'offline_data': {
                'type': 'assembly_audit',
                'id': str(form.instance.id),
                'data': {
                    'date': str(form.instance.date),
                    'shift': form.instance.shift,
                    'emp_id': form.instance.emp_id,
                    'name': form.instance.name,
                    'section': form.instance.section,
                    'line': form.instance.line,
                    'group': form.instance.group,
                    'model': form.instance.model,
                    'color': form.instance.color,
                }
            }
        }
        
        messages.success(self.request, "Audit record created successfully!")
        return render(self.request, 'ipqc/audit_success.html', context)
 
class IPQCAssemblyAuditUpdateView(RoleRequiredMixin, LoginRequiredMixin, UserCanEditAuditMixin, UpdateView):
    allowed_roles = ["IPQC"]
    model = IPQCAssemblyAudit
    form_class = IPQCAssemblyAuditForm
    template_name = 'ipqc/ipqc_assembly_audit_update_form.html'
    success_url = reverse_lazy('ipqc_audit_list')
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True
        form = context['form']
        
        context['machine_fields'] = [
            form['mach_epa_check'], form['mach_screw_torque'], form['mach_sholdering_temp'], 
            form['mach_light'], form['mach_fixture_clean'], form['mach_jig_label'], 
            form['mach_teflon'], form['mach_press_params'], form['mach_glue_params'],
            form['mach_eq_move_notify'], form['mach_feeler_gauge'], form['mach_hot_cold_press'], 
            form['mach_ion_fan'], form['mach_cleanroom_eq'], form['mach_rti_check'], 
            form['mach_current_test'], form['mach_pal_qr'], form['mach_auto_screw'],
        ]
 
        context['material_fields'] = [
            form['mat_key_check'], form['mat_special_stop'], form['mat_improved_monitor'], 
            form['mat_result_check'], form['mat_battery_issue'], form['mat_ipa_check'], 
            form['mat_thermal_gel'], form['mat_verification'],
        ]
 
        context['method_fields'] = [
            form['meth_sop_seq'], form['meth_distance_sensor'], form['meth_rear_camera'], 
            form['meth_material_handling'], form['meth_guideline_doc'], form['meth_operation_doc'], 
            form['meth_defective_feedback'], form['meth_line_record'], form['meth_no_self_repair'], 
            form['meth_battery_fix'], form['meth_line_change'], form['meth_trail_run'], 
            form['meth_dummy_conduct'],
        ]
 
        context['environment_fields'] = [
            form['env_prod_monitor'], form['env_5s'],
        ]
 
        context['trc_fields'] = [
            form['trc_flow_chart'], form['fai_check'], form['defect_monitor'], 
            form['spot_check'], form['auto_screw_sample'],
        ]
        
        context.update(get_pwa_context(self.request))
        return context
 
    def form_valid(self, form):
        form.instance.remarks = self.request.POST.get('remarks', '').strip()
        
        # PWA: Add data to context for frontend to save to IndexedDB
        context = {
            'offline_data': {
                'type': 'assembly_audit',
                'id': str(self.object.id),
                'data': {
                    'date': str(form.instance.date),
                    'shift': form.instance.shift,
                    'emp_id': form.instance.emp_id,
                    'name': form.instance.name,
                    'section': form.instance.section,
                    'line': form.instance.line,
                    'group': form.instance.group,
                    'model': form.instance.model,
                    'color': form.instance.color,
                }
            }
        }
 
        messages.success(self.request, "Audit record updated successfully!")
        return render(self.request, 'ipqc/audit_success.html', context)
 
class IPQCAssemblyAuditDeleteView(RoleRequiredMixin, LoginRequiredMixin, UserCanEditAuditMixin, DeleteView):
    allowed_roles = ["IPQC"]
    model = IPQCAssemblyAudit
    template_name = 'ipqc/confirm_delete.html'
    success_url = reverse_lazy('ipqc_audit_list')
 
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Audit record deleted successfully.")
        return super().delete(request, *args, **kwargs)
    
class BTBFitmentChecksheetCreateView(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    allowed_roles = ["IPQC"]
    model = BTBFitmentChecksheet
    form_class = BTBFitmentChecksheetForm
    template_name = 'ipqc/btb_checksheet_form.html'
    success_url = reverse_lazy('btb_checksheet_list')
 
    HOURS = ['9','10','11','12','1','2','3','4','5','6']
    
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        emp_id = getattr(user, 'employee_id', None)
 
        if emp_id:
            now = timezone.localtime()
            today = now.date()
            today_8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
            start_time = today_8am - timedelta(days=1) if now < today_8am else today_8am
            end_time = start_time + timedelta(days=1)
 
            has_filled = IPQCWorkInfo.objects.filter(
                emp_id=emp_id,
                created_at__range=[start_time, end_time]
            ).exists()
 
            if not has_filled:
                messages.warning(request, "⚠️ You haven't filled your Work Info for today. Please fill it before proceeding.")
                return redirect('ipqc_work_info')
 
        return super().dispatch(request, *args, **kwargs)
 
    def get_initial(self):
        initial = super().get_initial()
        emp_id = getattr(self.request.user, 'employee_id', None)
 
        initial['pqe_tl_sign'] = getattr(self.request.user, 'full_name', self.request.user.employee_id)
 
        if emp_id:
            try:
                latest_work_info = IPQCWorkInfo.objects. filter(emp_id=emp_id).latest('created_at')
                initial.update({
                    'date': latest_work_info.date, 'shift': latest_work_info.shift,
                    'emp_id': latest_work_info.emp_id, 'name': latest_work_info.name,
                    'section': latest_work_info.section, 'line': latest_work_info.line,
                    'group': latest_work_info.group, 'model': latest_work_info.model,
                    'color': latest_work_info.color,
                })
            except IPQCWorkInfo.DoesNotExist:
                messages.warning(self.request, "No Work Information found. Some fields may be empty.")
        
        return initial
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hours = ['9','10','11','12','1','2','3','4','5','6']
        context['hours'] = hours
        fields = {}
        for hour in hours:
            fields[hour] = {
                'input': f'input_{hour}',
                'cam_btb': f'cam_btb_{hour}',
                'lcd_fitment': f'lcd_fitment_{hour}',
                'main_fpc': f'main_fpc_{hour}',
                'battery': f'battery_{hour}',
                'finger_printer': f'finger_printer_{hour}',
            }
        context['hour_fields'] = fields
        context.update(get_pwa_context(self.request))
        return context
 
    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            messages.error(self.request, "You must be logged in to submit this form.")
            return self.form_invalid(form)
 
        try:
            user = self.request.user
            if not user.pk or not user.is_active:
                raise ValueError("Current user is invalid.")
        except Exception:
            messages.error(self.request, "Current user is invalid. Please contact admin.")
            return self.form_invalid(form)
 
        aggregated_data_json = self.request.POST.get('aggregated_data', '{}')
        try:
            aggregated_data = json.loads(aggregated_data_json)
        except json.JSONDecodeError:
            messages.error(self.request, "There was an error processing the form data. Please try again.")
            return self.form_invalid(form)
 
        for key, value in aggregated_data.items():
            if hasattr(form.instance, key):
                setattr(form.instance, key, value)
 
        form.instance.created_by = user
        
        # PWA: Add data to context for frontend to save to IndexedDB
        context = {
            'offline_data': {
                'type': 'btb_checksheet',
                'id': str(form.instance.id),
                'data': aggregated_data
            }
        }
 
        messages.success(self.request, "BTB Fitment Checksheet submitted successfully!")
        return render(self.request, 'ipqc/btb_checksheet_success.html', context)
 
class BTBFitmentChecksheetListView(RoleRequiredMixin, LoginRequiredMixin, ListView):
    allowed_roles = ["IPQC"]
    model = BTBFitmentChecksheet
    template_name = 'ipqc/btb_checksheet_list.html'
    context_object_name = 'checksheets'
    paginate_by = 10
 
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role.lower() == 'admin':
            return BTBFitmentChecksheet.objects. all()
        else:
            return BTBFitmentChecksheet.objects. filter(created_by=user)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_pwa_context(self.request))
        return context
        
class BTBFitmentChecksheetDetailView(RoleRequiredMixin, LoginRequiredMixin, DetailView):
    allowed_roles = ["IPQC"]
    model = BTBFitmentChecksheet
    template_name = 'ipqc/btb_checksheet_detail.html'
    context_object_name = 'sheet'
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_pwa_context(self.request))
        return context
    
class AssyDummyTestCreate(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    allowed_roles = ["IPQC"]
    model = AssDummyTest
    form_class = AssDummyTestForm
    template_name = 'ipqc/ass_dummy_test_form.html'
    success_url = reverse_lazy('ass_dummy_test_list')
    
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        emp_id = getattr(user, 'employee_id', None)
 
        if emp_id:
            now = timezone.localtime()
            today = now.date()
            today_8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
            start_time = today_8am - timedelta(days=1) if now < today_8am else today_8am
            end_time = start_time + timedelta(days=1)
 
            has_filled = IPQCWorkInfo.objects.filter(
                emp_id=emp_id,
                created_at__range=[start_time, end_time]
            ).exists()
 
            if not has_filled:
                messages.warning(request, "⚠️ You haven't filled your Work Info for today. Please fill it before proceeding.")
                return redirect('ipqc_work_info')
 
        return super().dispatch(request, *args, **kwargs)
 
    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
 
        initial['pqe_tl_sign'] = getattr(user, 'full_name', getattr(user, 'employee_id', ''))
 
        emp_id = getattr(user, 'employee_id', None)
        if emp_id:
            try:
                latest_work_info = IPQCWorkInfo.objects.filter(emp_id=emp_id).latest('created_at')
                initial.update({
                    'date': latest_work_info.date,
                    'shift': latest_work_info.shift,
                    'emp_id': latest_work_info.emp_id,
                    'name': latest_work_info.name,
                    'section': latest_work_info.section,
                    'line': latest_work_info.line,
                    'group': latest_work_info.group,
                    'model': latest_work_info.model,
                    'color': latest_work_info.color,
                })
            except IPQCWorkInfo.DoesNotExist:
                messages.warning(self.request, "No Work Information found. Some fields may be empty.")
        return initial
 
    def form_valid(self, form):
        user = self.request.user
        aggregated_data_json = self.request.POST.get('aggregated_data', '{}')
        try:
            aggregated_data = json.loads(aggregated_data_json)
        except json.JSONDecodeError:
            messages.error(self.request, "Error processing form data. Please try again.")
            return self.form_invalid(form)

        sensitive_fields = {'id', 'pk', 'created_by', 'updated_at', 'created_at'}
        for key, value in aggregated_data.items():
            if hasattr(form.instance, key) and key not in sensitive_fields:
                setattr(form.instance, key, value)

        form.instance.created_by = user
        
        # PWA: Add data to context for frontend to save to IndexedDB
        context = {
            'offline_data': {
                'type': 'ass_dummy_test',
                'id': str(form.instance.id),
                'data': aggregated_data
            }
        }

        messages.success(self.request, "Assy Dummy Test submitted successfully!")
        return render(self.request, 'ipqc/ass_dummy_test_success.html', context)
    
class AssDummyTestListView(RoleRequiredMixin, LoginRequiredMixin, ListView):
    allowed_roles = ["IPQC"]
    model = AssDummyTest
    template_name = 'ipqc/ass_dummy_test_list.html'
    context_object_name = 'tests'
    ordering = ['-date', '-id']
    paginate_by = 25
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_pwa_context(self.request))
        return context
    
class IPQCDisassembleCheckListCreateView(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    allowed_roles = ["IPQC"]
    model = IPQCDisassembleCheckList
    form_class = IPQCDisassembleCheckListForm
    template_name = 'ipqc/ipqc_disassemble_form.html'
    success_url = reverse_lazy('ipqc_disassemble_list')
    
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        emp_id = getattr(user, 'employee_id', None)

        if emp_id:
            now = timezone.localtime()
            today = now.date()
            today_8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
            start_time = today_8am - timedelta(days=1) if now < today_8am else today_8am
            end_time = start_time + timedelta(days=1)

            has_filled = IPQCWorkInfo.objects.filter(
                emp_id=emp_id,
                created_at__range=[start_time, end_time]
            ).exists()

            if not has_filled:
                messages.warning(request, "⚠️ You haven't filled your Work Info for today. Please fill it before proceeding.")
                return redirect('ipqc_work_info')

        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        emp_id = getattr(user, 'employee_id', None)

        if emp_id:
            try:
                latest_work_info = IPQCWorkInfo.objects.filter(emp_id=emp_id).latest('created_at')
                initial.update({
                    'date': latest_work_info.date,
                    'shift': latest_work_info.shift,
                    'emp_id': latest_work_info.emp_id,
                    'name': latest_work_info.name,
                    'section': latest_work_info.section,
                    'line': latest_work_info.line,
                    'group': latest_work_info.group,
                    'model': latest_work_info.model,
                    'color': latest_work_info.color,
                })
            except IPQCWorkInfo.DoesNotExist:
                messages.warning(self.request, "⚠️ No Work Information found. Some fields may be empty.")
        else:
            messages.warning(self.request, "⚠️ Employee ID missing. Please ensure your profile is complete.")
        return initial

    def form_valid(self, form):
        if hasattr(form.instance, 'created_by'):
            form.instance.created_by = self.request.user
            
        # PWA: Add data to context for frontend to save to IndexedDB
        context = {
            'offline_data': {
                'type': 'disassemble_checklist',
                'id': str(form.instance.id),
                'data': {
                    'date': str(form.instance.date),
                    'shift': form.instance.shift,
                    'emp_id': form.instance.emp_id,
                    'name': form.instance.name,
                    'section': form.instance.section,
                    'line': form.instance.line,
                    'group': form.instance.group,
                    'model': form.instance.model,
                    'color': form.instance.color,
                }
            }
        }

        messages.success(self.request, "✅ IPQC Disassemble Checklist submitted successfully!")
        return render(self.request, 'ipqc/disassemble_success.html', context)

    def form_invalid(self, form):
        messages.error(self.request, "❌ Please correct the highlighted errors before submitting.")
        return super().form_invalid(form)

class IPQCDisassembleCheckListView(RoleRequiredMixin, LoginRequiredMixin, ListView):
    allowed_roles = ["IPQC"]
    model = IPQCDisassembleCheckList
    template_name = 'ipqc/ipqc_disassemble_list.html'
    context_object_name = 'records'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-created_at')
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(emp_id__icontains=query) |
                Q(model__icontains=query) |
                Q(color__icontains=query)
            )
        return queryset
    
    def get_overall_status(self):
        choice_fields = [field.name for field in self._meta.fields 
                        if field.choices and field.name not in ['created_by']]
        
        ok_count = 0
        not_ok_count = 0
        total_checked = 0
        
        for field_name in choice_fields:
            value = getattr(self, field_name)
            if value == 'OK':
                ok_count += 1
                total_checked += 1
            elif value == 'Not OK':
                not_ok_count += 1
                total_checked += 1
        
        if total_checked == 0:
            return 'MIXED'
        elif not_ok_count == 0:
            return 'PASS'
        elif ok_count == 0:
            return 'FAIL'
        else:
            return 'MIXED'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        today = timezone.now().date()
        week_start = today - datetime.timedelta(days=today.weekday())
        
        all_records = self.model.objects.all()
        
        stats = {
            'today': all_records.filter(created_at__date=today).count(),
            'week': all_records.filter(created_at__date__gte=week_start).count(),
            'total': all_records.count(),
        }
        
        context['ipqc_disassemble_stats'] = stats
        context['total_records'] = stats['total']
        context['recent_submissions'] = self.model.objects.order_by('-created_at')[:5]
        context.update(get_pwa_context(self.request))
        
        return context
    
class IPQCDisassembleDetailView(DetailView):
    model = IPQCDisassembleCheckList
    
    def get(self, request, *args, **kwargs):
        try:
            record = self.get_object()
            
            data = {
                'date': record.date.strftime('%Y-%m-%d'),
                'shift': record.shift,
                'emp_id': record.emp_id,
                'name': record.name,
                'section': record.section,
                'line': record.line,
                'group': record.group,
                'model': record.model,
                'color': record.color,
                'color_match': record.color_match,
                'cam_lens_assembly': record.cam_lens_assembly,
                'cam_lens_cleanliness': record.cam_lens_cleanliness,
                'key_feel': record.key_feel,
                'key_alignment': record.key_alignment,
                'screw_missing': record.screw_missing,
                'screw_loose': record.screw_loose,
                'screw_spec': record.screw_spec,
                'front_housing_damage': record.front_housing_damage,
                'back_housing_damage': record.back_housing_damage,
                'housing_snap_fit': record.housing_snap_fit,
                'proof_label_position': record.proof_label_position,
                'tp_sop': record.tp_sop,
                'mic_solder': record.mic_solder,
                'led_solder': record.led_solder,
                'lcd_stick': record.lcd_stick,
                'speaker_solder': record.speaker_solder,
                'motor_solder': record.motor_solder,
                'key_solder': record.key_solder,
                'sim_subboard_solder': record.sim_subboard_solder,
                'subboard_solder': record.subboard_solder,
                'camera_solder': record.camera_solder,
                'receiver_solder': record.receiver_solder,
                'coaxial_line': record.coaxial_line,
                'antenna_shrapnel': record.antenna_shrapnel,
                'antenna_fpc': record.antenna_fpc,
                'conductive_fabric': record.conductive_fabric,
                'insulation_paste': record.insulation_paste,
                'ins_paste_cover': record.ins_paste_cover,
                'lcd_fpc_defect': record.lcd_fpc_defect,
                'tp_fpc_defect': record.tp_fpc_defect,
                'key_fpc_solder': record.key_fpc_solder,
                'keypad_defect': record.keypad_defect,
                'mainboard_component_ok': record.mainboard_component_ok,
                'solder_splash': record.solder_splash,
                'foam_stick': record.foam_stick,
                'cam_glue': record.cam_glue,
                'led_position': record.led_position,
                'jig_fixture_test': record.jig_fixture_test,
                'glue_location': record.glue_location,
                'glue_weight_1': str(record.glue_weight_1) if record.glue_weight_1 else None,
                'glue_weight_2': str(record.glue_weight_2) if record.glue_weight_2 else None,
                'glue_weight_3': str(record.glue_weight_3) if record.glue_weight_3 else None,
                'defect_cause': record.defect_cause,
                'imei1': record.imei1,
                'imei2': record.imei2,
                'pqe': record.pqe,
                'pe': record.pe,
                'apd_ll': record.apd_ll,
                'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'photos': []
            }
            
            photo_fields = [
                ('color_match_photo', 'Color Match Photo'),
                ('cam_lens_photo', 'Camera Lens Photo'),
                ('key_photo', 'Keys Photo'),
                ('screw_photo', 'Screw Photo'),
                ('housing_photo', 'Housing Photo'),
                ('proof_label_photo', 'Proof Label Photo'),
                ('assembly_overview_photo', 'Assembly Overview'),
                ('defect_photo', 'Defect Photo'),
            ]
            
            for field_name, label in photo_fields:
                photo = getattr(record, field_name)
                if photo:
                    data['photos'].append({
                        'label': label,
                        'url': photo.url
                    })
            
            return JsonResponse(data)
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error loading IPQC Disassemble details: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)    

class NCIssueTrackingCreateView(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    allowed_roles = ["IPQC"]
    model = NCIssueTracking
    form_class = NCIssueTrackingForm
    template_name = 'ipqc/nc_issue_tracking_form.html'
    success_url = reverse_lazy('nc_issue_tracking_list')
    
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        emp_id = getattr(user, 'employee_id', None)

        if emp_id:
            now = timezone.localtime()
            today = now.date()
            today_8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
            start_time = today_8am - timedelta(days=1) if now < today_8am else today_8am
            end_time = start_time + timedelta(days=1)

            has_filled = IPQCWorkInfo.objects.filter(
                emp_id=emp_id,
                created_at__range=[start_time, end_time]
            ).exists()

            if not has_filled:
                messages.warning(request, "⚠️ You haven't filled your Work Info for today. Please fill it before proceeding.")
                return redirect('ipqc_work_info')

        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user

        emp_id = getattr(user, 'employee_id', None)
        if emp_id:
            try:
                latest_work_info = IPQCWorkInfo.objects.filter(emp_id=emp_id).latest('created_at')
                initial.update({
                    'date': latest_work_info.date,
                    'shift': latest_work_info.shift,
                    'emp_id': latest_work_info.emp_id,
                    'name': latest_work_info.name,
                    'section': latest_work_info.section,
                    'line': latest_work_info.line,
                    'group': latest_work_info.group,
                    'model': latest_work_info.model,
                    'color': latest_work_info.color,
                })
            except IPQCWorkInfo.DoesNotExist:
                messages.warning(self.request, "⚠️ No Work Information found. Some fields may be empty.")
        return initial

    def form_valid(self, form):
        user = self.request.user

        aggregated_data_json = self.request.POST.get('aggregated_data', '{}')
        try:
            aggregated_data = json.loads(aggregated_data_json)
        except json.JSONDecodeError:
            messages.error(self.request, "Error processing form data. Please try again.")
            return self.form_invalid(form)

        sensitive_fields = {'id', 'pk', 'created_at', 'updated_at'}
        for key, value in aggregated_data.items():
            if hasattr(form.instance, key) and key not in sensitive_fields:
                setattr(form.instance, key, value)

        if hasattr(form.instance, 'created_by'):
            form.instance.created_by = user
            
        # PWA: Add data to context for frontend to save to IndexedDB
        context = {
            'offline_data': {
                'type': 'nc_issue_tracking',
                'id': str(form.instance.id),
                'data': aggregated_data
            }
        }

        messages.success(self.request, "✅ NC Issue Tracking submitted successfully!")
        return render(self.request, 'ipqc/nc_issue_success.html', context)
    
class NCIssueTrackingListView(RoleRequiredMixin, LoginRequiredMixin, ListView):
    allowed_roles = ["IPQC"]
    model = NCIssueTracking
    template_name = 'ipqc/nc_issue_tracking_list.html'
    context_object_name = 'records'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-created_at')
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(emp_id__icontains=query) |
                Q(model__icontains=query) |
                Q(color__icontains=query)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_pwa_context(self.request))
        return context
    
class ESDComplianceChecklistCreateView(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    allowed_roles = ["IPQC"]
    model = ESDComplianceChecklist
    form_class = ESDComplianceChecklistForm
    template_name = 'ipqc/esd_compliance_checklist_form.html'
    success_url = reverse_lazy('esd_compliance_checklist_list')
    
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        emp_id = getattr(user, 'employee_id', None)

        if emp_id:
            now = timezone.localtime()
            today = now.date()
            today_8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
            start_time = today_8am - timedelta(days=1) if now < today_8am else today_8am
            end_time = start_time + timedelta(days=1)

            has_filled = IPQCWorkInfo.objects.filter(
                emp_id=emp_id,
                created_at__range=[start_time, end_time]
            ).exists()

            if not has_filled:
                messages.warning(request, "⚠️ You haven't filled your Work Info for today. Please fill it before proceeding.")
                return redirect('ipqc_work_info')

        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        emp_id = getattr(user, 'employee_id', None)

        if emp_id:
            try:
                latest_work_info = IPQCWorkInfo.objects.filter(emp_id=emp_id).latest('created_at')
                initial.update({
                    'date': latest_work_info.date,
                    'shift': latest_work_info.shift,
                    'emp_id': latest_work_info.emp_id,
                    'name': latest_work_info.name,
                    'line': latest_work_info.line,
                    'group': latest_work_info.group,
                    'model': latest_work_info.model,
                    'color': latest_work_info.color,
                })
            except IPQCWorkInfo.DoesNotExist:
                messages.warning(self.request, "⚠️ No Work Information found. Some fields may be empty.")
        else:
            messages.warning(self.request, "⚠️ No Employee ID found for current user.")

        return initial

    def form_valid(self, form):
        if hasattr(form.instance, 'created_by'):
            form.instance.created_by = self.request.user
            
        # PWA: Add data to context for frontend to save to IndexedDB
        context = {
            'offline_data': {
                'type': 'esd_compliance',
                'id': str(form.instance.id),
                'data': {
                    'date': str(form.instance.date),
                    'shift': form.instance.shift,
                    'emp_id': form.instance.emp_id,
                    'name': form.instance.name,
                    'section': form.instance.section,
                    'line': form.instance.line,
                    'group': form.instance.group,
                    'model': form.instance.model,
                    'color': form.instance.color,
                }
            }
        }
        
        response = super().form_valid(form)
        messages.success(self.request, "✅ ESD Compliance Checklist submitted successfully!")
        return render(self.request, 'ipqc/esd_success.html', context)

class ESDComplianceCheckListView(RoleRequiredMixin, LoginRequiredMixin, ListView):
    allowed_roles = ["IPQC", "admin", "superuser"]
    model = ESDComplianceChecklist
    template_name = 'ipqc/esd_compliance_checklist_list.html'
    context_object_name = 'records'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-date', '-created_at')
        search_query = self.request.GET.get('q')

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(emp_id__icontains=search_query) |
                Q(line__icontains=search_query) |
                Q(model__icontains=search_query)
            )

        return queryset
    
    def get_overall_status(self):
        audit_fields = [f.name for f in self._meta.fields if f.choices]
        
        ok_count = 0
        not_ok_count = 0
        na_count = 0
        
        for field_name in audit_fields:
            value = getattr(self, field_name)
            if value == 'OK':
                ok_count += 1
            elif value == 'NOT_OK':
                not_ok_count += 1
            elif value == 'NA':
                na_count += 1

        if not_ok_count > 0:
            return 'FAIL'
        if ok_count > 0 and na_count > 0:
            return 'MIXED'
        if ok_count > 0:
            return 'PASS'
        return 'N/A'

    def __str__(self):
        return f"{self.date} - {self.line} - {self.name}"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        base_queryset = self.model.objects.all()
        today = timezone.now().date()
        
        context['total_records'] = base_queryset.count()
        context['today_records'] = base_queryset.filter(date=today).count()
        
        start_of_week = today - timedelta(days=today.weekday())
        context['week_records'] = base_queryset.filter(date__gte=start_of_week).count()
        
        context.update(get_pwa_context(self.request))
        return context

@require_GET
def esd_compliance_checklist_details(request, pk):
    record = get_object_or_404(ESDComplianceChecklist, pk=pk)
    
    def get_verbose_name(field_name):
        try:
            return record._meta.get_field(field_name).verbose_name
        except:
            return field_name.replace('_', ' ').title()

    basic_info = {
        'date': {'label': 'Date', 'value': record.date.strftime('%d-%m-%Y')},
        'shift': {'label': 'Shift', 'value': record.shift},
        'emp_id': {'label': 'Employee ID', 'value': record.emp_id},
        'name': {'label': 'Employee Name', 'value': record.name},
        'line': {'label': 'Line', 'value': record.line},
        'group': {'label': 'Group', 'value': record.group},
        'model': {'label': 'Model', 'value': record.model},
        'color': {'label': 'Color', 'value': record.color},
    }
    
    sections = {
        'clothing': {
            'title': 'Clothing Rules', 'icon': 'fa-tshirt',
            'fields': [
                'epa_clothes', 'forbid_wear_out', 'no_accessories', 'clothes_clean',
                'collar_cover', 'all_buttons_closed', 'clothes_length', 'watch_expose', 'hair_cap'
            ]
        },
        'wristband': {
            'title': 'Wristband & Slipper', 'icon': 'fa-hand-paper',
            'fields': ['slipper_check', 'wristband_check', 'pre_line_check', 'wrist_touch_skin']
        },
        'handling': {
            'title': 'Handling Rules', 'icon': 'fa-hand-sparkles',
            'fields': ['no_touch_pcba', 'alert_plug_out']
        },
        'grounding': {
            'title': 'Grounding & Equipment', 'icon': 'fa-plug',
            'fields': ['trolley_grounding', 'device_grounded', 'grounding_points_tight', 'ion_fan_distance', 'ion_fan_direction']
        },
        'consumables': {
            'title': 'Consumables', 'icon': 'fa-box',
            'fields': ['gloves_condition', 'mat_grounded', 'audit_label_valid']
        },
        'material': {
            'title': 'Material Handling', 'icon': 'fa-boxes',
            'fields': ['esds_box', 'table_no_source']
        },
        'tools': {
            'title': 'Tools & Environment', 'icon': 'fa-tools',
            'fields': ['tools_audit', 'temp_humidity', 'tray_voltage']
        }
    }
    
    compliance_data = {}
    for key, section in sections.items():
        compliance_data[key] = {
            'title': section['title'],
            'icon': section['icon'],
            'items': []
        }
        for field_name in section['fields']:
            compliance_data[key]['items'].append({
                'label': get_verbose_name(field_name),
                'value': getattr(record, field_name),
            })

    readings = {
        'temperature_value': {'label': 'Temperature (°C)', 'value': record.temperature_value},
        'humidity_value': {'label': 'Humidity (%)', 'value': record.humidity_value},
        'tray_voltage_value': {'label': 'Tray Voltage (V)', 'value': record.tray_voltage_value},
    }
    
    photo_fields = {
        'epa_clothes_photo': 'EPA Clothes',
        'hair_cap_photo': 'Hair Cap',
        'wristband_photo': 'Wristband',
        'trolley_photo': 'Trolley Grounding',
        'ion_fan_photo': 'Ion Fan',
        'mat_photo': 'ESD Mat',
        'table_photo': 'Working Table',
        'photo_overview': 'Overview'
    }
    available_photos = []
    for field, label in photo_fields.items():
        photo = getattr(record, field)
        if photo:
            url = photo.url if photo.url.startswith('/media/') else f"{settings.MEDIA_URL}{photo}"
            available_photos.append({'url': url, 'label': label})

    overall_status = 'N/A'
    if hasattr(record, 'get_overall_status'):
        overall_status = record.get_overall_status()

    data = {
        'basic_info': basic_info,
        'compliance': compliance_data,
        'readings': readings,
        'photos': available_photos,
        'remark': record.remark,
        'overall_status': overall_status,
        'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S'),
    }
    return JsonResponse(data)
    
class DustCountCreateView(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    allowed_roles = ["IPQC"]
    model = DustCountCheck
    form_class = DustCountCheckForm
    template_name = 'ipqc/dust_count_checklist_form.html'
    success_url = reverse_lazy('dust_count_checklist_list')
    
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        emp_id = getattr(user, 'employee_id', None)

        if emp_id:
            now = timezone.localtime()
            today = now.date()
            today_8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
            start_time = today_8am - timedelta(days=1) if now < today_8am else today_8am
            end_time = start_time + timedelta(days=1)

            has_filled = IPQCWorkInfo.objects.filter(
                emp_id=emp_id,
                created_at__range=[start_time, end_time]
            ).exists()

            if not has_filled:
                messages.warning(request, "⚠️ You haven't filled your Work Info for today. Please fill it before proceeding.")
                return redirect('ipqc_work_info')

        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        emp_id = getattr(user, 'employee_id', None)
        if emp_id:
            try:
                latest_work_info = IPQCWorkInfo.objects.filter(emp_id=emp_id).latest('created_at')
                initial.update({
                    'date': latest_work_info.date,
                    'shift': latest_work_info.shift,
                    'emp_id': latest_work_info.emp_id,
                    'name': latest_work_info.name,
                    'section': latest_work_info.section,
                    'line': latest_work_info.line,
                    'group': latest_work_info.group,
                    'model': latest_work_info.model,
                    'color': latest_work_info.color,
                })
            except IPQCWorkInfo.DoesNotExist:
                messages.warning(self.request, "⚠️ No Work Information found. Some fields may be empty.")
        return initial

    def form_valid(self, form):
        if hasattr(form.instance, 'created_by'):
            form.instance.created_by = self.request.user
            
        # PWA: Add data to context for frontend to save to IndexedDB
        context = {
            'offline_data': {
                'type': 'dust_count',
                'id': str(form.instance.id),
                'data': {
                    'date': str(form.instance.date),
                    'shift': form.instance.shift,
                    'emp_id': form.instance.emp_id,
                    'name': form.instance.name,
                    'section': form.instance.section,
                    'line': form.instance.line,
                    'group': form.instance.group,
                    'model': form.instance.model,
                    'color': form.instance.color,
                }
            }
        }
        
        response = super().form_valid(form)
        messages.success(self.request, "✅ Dust Count Check submitted successfully!")
        return render(self.request, 'ipqc/dust_count_success.html', context)

class DustCountListView(ListView):
    model = DustCountCheck
    template_name = 'ipqc/dust_count_checklist_list.html'
    context_object_name = 'records'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-date', '-created_at')
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(emp_id__icontains=search_query) |
                Q(line__icontains=search_query)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_pwa_context(self.request))
        return context
    
class TestingFirstArticleInspectionCreateView(LoginRequiredMixin, CreateView):
    model = TestingFirstArticleInspection
    form_class = TestingFirstArticleInspectionForm
    template_name = 'ipqc/testing_fai_form.html'
    success_url = reverse_lazy('testing_fai_list')
    
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        emp_id = getattr(user, 'employee_id', None)

        if emp_id:
            now = timezone.localtime()
            today = now.date()
            today_8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
            start_time = today_8am - timedelta(days=1) if now < today_8am else today_8am
            end_time = start_time + timedelta(days=1)

            has_filled = IPQCWorkInfo.objects.filter(
                emp_id=emp_id,
                created_at__range=[start_time, end_time]
            ).exists()

            if not has_filled:
                messages.warning(request, "⚠️ You haven't filled your Work Info for today. Please fill it before proceeding.")
                return redirect('ipqc_work_info')

        return super().dispatch(request, *args, **kwargs)
    
    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        emp_id = getattr(user, 'employee_id', None)
        if emp_id:
            try:
                latest_work_info = IPQCWorkInfo.objects. filter(emp_id=emp_id).latest('created_at')
                initial.update({
                    'date': latest_work_info.date, 'shift': latest_work_info.shift,
                    'emp_id': latest_work_info.emp_id, 'name': latest_work_info.name,
                    'section': getattr(latest_work_info, 'section', ''), 'line': latest_work_info.line,
                    'group': latest_work_info.group, 'model': latest_work_info.model,
                    'color': latest_work_info.color,
                })
            except IPQCWorkInfo.DoesNotExist:
                messages.warning(self.request, "⚠️ No pre-filled work information found.")
        initial['inspector_name'] = getattr(user, 'full_name', None) or user.username
        return initial
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        response = super().form_valid(form)
        instance = self.object
        public_link = self.request.build_absolute_uri(reverse('testing_fai_public_update', args=[str(instance.public_token)]))
        instance.public_url = public_link
        instance.save(update_fields=['public_url'])
        
        # PWA: Add data to context for frontend to save to IndexedDB
        context = {
            'offline_data': {
                'type': 'fai_inspection',
                'id': str(instance.id),
                'data': {
                    'date': str(instance.date),
                    'shift': instance.shift,
                    'emp_id': instance.emp_id,
                    'name': instance.name,
                    'section': instance.section,
                    'line': instance.line,
                    'group': instance.group,
                    'model': instance.model,
                    'color': instance.color,
                    'inspector_name': instance.inspector_name,
                }
            }
        }
        
        messages.success(self.request, f"✅ Record created! QE link generated.")
        return render(self.request, 'ipqc/fai_success.html', context)
    
    def form_invalid(self, form):
        messages.error(self.request, "❌ Error creating FAI record. Please check the form for errors.")
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'First Article Inspection (FAI)'
        context['breadcrumbs'] = [
            {'name': 'dashboard', 'url': reverse_lazy('ipqc_home')},
            {'name': 'FAI List', 'url': reverse_lazy('testing_fai_list')},
            {'name': 'New FAI', 'url': reverse_lazy('testing_fai_create')},
        ]
        context.update(get_pwa_context(self.request))
        return context
 
class TestingFirstArticleInspectionListView(LoginRequiredMixin, ListView):
    model = TestingFirstArticleInspection
    template_name = 'ipqc/testing_fai_list.html'
    context_object_name = 'fai_records'
    paginate_by = 10
    ordering = ['-date', '-created_at']
 
    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')

        if search_query:
            queryset = queryset.filter(
                Q(inspector_name__icontains=search_query) |
                Q(model__icontains=search_query) |
                Q(color__icontains=search_query) |
                Q(imei_number__icontains=search_query)
            )

        if user.is_superuser or user.groups.filter(name__in=['Admin', 'QA']).exists():
            return queryset
        else:
            inspector_name = getattr(user, 'full_name', None) or getattr(user, 'name', None) or getattr(user, 'username', None) or str(user)
            return queryset.filter(inspector_name=inspector_name)
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        queryset_for_stats = self.get_queryset()
        
        today = timezone.now().date()
        week_start = today - timezone.timedelta(days=today.weekday())
        
        context.update({
            'page_title': 'FAI Records',
            'fai_stats': {
                'today': queryset_for_stats.filter(date=today).count(),
                'week': queryset_for_stats.filter(date__gte=week_start).count(),
                'total': queryset_for_stats.count(),
            },
            'breadcrumbs': [
                {'name': 'Dashboard', 'url': reverse_lazy('ipqc_home')}, 
                {'name': 'FAI List', 'url': '#'}
            ]
        })
        context.update(get_pwa_context(self.request))
        return context
 
class TestingFirstArticleInspectionDetailView(LoginRequiredMixin, DetailView):
    model = TestingFirstArticleInspection
    template_name = 'ipqc/testing_fai_detail.html'
    context_object_name = 'fai_record'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': f'FAI Detail - {self.object.model}',
            'breadcrumbs': [
                {'name': 'dashboard', 'url': reverse_lazy('ipqc_home')},
                {'name': 'FAI List', 'url': reverse_lazy('testing_fai_list')},
                {'name': f'{self.object.model}', 'url': '#'}
            ]
        })
        context.update(get_pwa_context(self.request))
        return context
 
def download_testing_fai_evidence(request, pk, evidence_type):
    fai = get_object_or_404(TestingFirstArticleInspection, pk=pk)
    if not (request.user.is_superuser or 
            request.user.groups.filter(name__in=['Admin', 'QA']).exists() or
            fai.inspector_name == (request.user.get_full_name() or request.user.username)):
        raise Http404("Permission denied.")
 
    evidence_fields = {
        'label_photo': fai.label_check_evidence, 
        'label_position_photo': fai.label_position_check_evidence,
        'logo_photo': fai.logo_check_evidence, 
        'assembly_photo': fai.assembly_battery_check_evidence,
        'boot_video': fai.boot_time_test_evidence, 
        'cam_front_photo': fai.camera_front_test_evidence,
        'cam_back_photo': fai.camera_back_test_evidence, 
        'cam_dark_photo': fai.camera_dark_test_evidence,
        'temp_cam_photo': fai.high_temp_camera_test_evidence, 
        'imei_photo': fai.imei_photo,
    }
    file = evidence_fields.get(evidence_type)
    if not file or not file.name:
        raise Http404("Evidence file not found.")
    
    response = HttpResponse(file.read(), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file.name)}"'
    return response
 

def testing_fai_public_qe_update_view(request, public_token):
    fai_record = get_object_or_404(TestingFirstArticleInspection, public_token=public_token)
    if request.method == "POST":
        qe_name = request.POST.get("qe_confirm_name")
        qe_status = request.POST.get("qe_confirm_status")
        if qe_name and qe_status:
            fai_record.qe_confirm_name = qe_name
            fai_record.qe_confirm_status = qe_status
            if not fai_record.public_url:
                fai_record.public_url = request.build_absolute_uri(reverse('testing_fai_public_update', args=[str(fai_record.public_token)]))
            fai_record.save(update_fields=["qe_confirm_name", "qe_confirm_status", "public_url"])
            messages.success(request, "✅ QE confirmation submitted successfully.")
            return redirect(request.path)
        else:
            messages.error(request, "⚠️ Please fill all required fields.")
    return render(request, "ipqc/testing_fai_public_qe_update.html", {"fai_record": fai_record})
 
class TestingFAIDetailsJsonView(LoginRequiredMixin, DetailView):
    model = TestingFirstArticleInspection
    
    def render_to_response(self, context, **response_kwargs):
        obj = self.get_object()
        data = {
            'date': obj.date.strftime('%Y-%m-%d'),
            'Shift': obj.shift, 'EMP_ID': obj.emp_id, 'Name': obj.name,
            'section': obj.section, 'line': obj.line, 'group': obj.group,
            'model': obj.model, 'color': obj.color,
            'production_work_order_no': obj.production_work_order_no,
            'first_article_type': obj.get_first_article_type_display(),
            'visual_functional_result': obj.visual_functional_result,
            'reliability_result': obj.reliability_result,
            'qe_confirm_name': obj.qe_confirm_name,
            'qe_confirm_status': obj.qe_confirm_status,
            'inspector_name': obj.inspector_name,
            'sample_serial_number': obj.sample_serial_number,
            'imei_number': obj.imei_number,
            'public_url': obj.public_url,
            'created_at': obj.created_at.strftime('%Y-%m-%d %H:%M'),
            'photos': []
        }
        
        for field in obj._meta.fields:
            if field.name.endswith(('_check', '_test')) and field.choices:
                data[field.name] = getattr(obj, field.name)
        
        photo_labels = {
            'label_check_evidence': 'Label Check Photo',
            'label_position_check_evidence': 'Label Position Photo',
            'logo_check_evidence': 'Logo Photo',
            'assembly_battery_check_evidence': 'Assembly Photo',
            'camera_front_test_evidence': 'Front Camera Photo',
            'camera_back_test_evidence': 'Back Camera Photo',
            'camera_dark_test_evidence': 'Dark Condition Photo',
            'high_temp_camera_test_evidence': 'High Temp Camera Photo',
            'imei_photo': 'IMEI Verification Photo'
        }
        for field_name, label in photo_labels.items():
            file = getattr(obj, field_name)
            if file:
                data['photos'].append({'url': file.url, 'label': label})
 
        return JsonResponse(data)

class OperatorQualificationCheckCreateView(CreateView):
    model = OperatorQualificationCheck
    form_class = OperatorQualificationCheckForm
    template_name = "ipqc/operator_qualification_form.html"
    success_url = reverse_lazy("operator_qualification_list")
    
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        emp_id = getattr(user, 'employee_id', None)

        if emp_id:
            now = timezone.localtime()
            today = now.date()
            today_8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
            start_time = today_8am - timedelta(days=1) if now < today_8am else today_8am
            end_time = start_time + timedelta(days=1)

            has_filled = IPQCWorkInfo.objects.filter(
                emp_id=emp_id,
                created_at__range=[start_time, end_time]
            ).exists()

            if not has_filled:
                messages.warning(request, "⚠️ You haven't filled your Work Info for today. Please fill it before proceeding.")
                return redirect('ipqc_work_info')

        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        emp_id = getattr(user, 'employee_id', None)
        if emp_id:
            try:
                latest_work_info = IPQCWorkInfo.objects.filter(emp_id=emp_id).latest('created_at')
                initial.update({
                    'date': latest_work_info.date, 'shift': latest_work_info.shift,
                    'emp_id': latest_work_info.emp_id, 'name': latest_work_info.name,
                    'section': getattr(latest_work_info, 'section', ''), 'line': latest_work_info.line,
                    'group': latest_work_info.group, 'model': latest_work_info.model,
                    'color': latest_work_info.color,
                })
            except IPQCWorkInfo.DoesNotExist:
                messages.warning(self.request, "⚠️ No pre-filled work information found.")
        return initial

    def form_valid(self, form):
        scanned_url = self.request.POST.get("scanned_result")
        if scanned_url:
            form.instance.scanned_barcode_text = scanned_url
            messages.success(self.request, "✅ QR/Barcode scanned and saved successfully.")
        else:
            messages.warning(self.request, "⚠️ No QR/Barcode scanned.")
            
        # PWA: Add data to context for frontend to save to IndexedDB
        context = {
            'offline_data': {
                'type': 'operator_qualification',
                'id': str(form.instance.id),
                'data': {
                    'date': str(form.instance.date),
                    'shift': form.instance.shift,
                    'emp_id': form.instance.emp_id,
                    'name': form.instance.name,
                    'section': form.instance.section,
                    'line': form.instance.line,
                    'group': form.instance.group,
                    'model': form.instance.model,
                    'color': form.instance.color,
                }
            }
        }
        
        return render(self.request, 'ipqc/operator_qualification_success.html', context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scanned_url = self.request.GET.get("scanned_url")
        if scanned_url:
            context["scanned_url"] = scanned_url
        context.update(get_pwa_context(self.request))
        return context

class OperatorQualificationCheckListView(ListView):
    model = OperatorQualificationCheck
    template_name = 'ipqc/operator_qualification_list.html'
    context_object_name = 'records'
    ordering = ['-created_at']
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                models.Q(emp_id__icontains=q) |
                models.Q(name__icontains=q) |
                models.Q(model__icontains=q) |
                models.Q(color__icontains=q) |
                models.Q(line__icontains=q)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        context['stats'] = {
            'today': OperatorQualificationCheck.objects.filter(date=today).count(),
            'week': OperatorQualificationCheck.objects.filter(date__gte=week_ago).count(),
            'total': OperatorQualificationCheck.objects.count(),
        }
        
        context.update(get_pwa_context(self.request))
        return context

def operator_qualification_detail(request, pk):
    record = get_object_or_404(OperatorQualificationCheck, pk=pk)
    
    data = {
        'date': record.date.strftime('%Y-%m-%d'),
        'shift': record.shift,
        'emp_id': record.emp_id,
        'name': record.name,
        'section': record.section,
        'line': record.line,
        'group': record.group,
        'model': record.model,
        'color': record.color,
        'key_station_name': record.key_station_name,
        'key_station_job_card_status': record.key_station_job_card_status,
        'key_station_operator_status': record.key_station_operator_status,
        'new_or_rotating_operator_status': record.new_or_rotating_operator_status,
        'check_operator_work_instruction': record.check_operator_work_instruction,
        'pqe_training_and_verification_status': record.pqe_training_and_verification_status,
        'job_card_verification_summary': record.job_card_verification_summary,
        'scanned_barcode_text': record.scanned_barcode_text,
        'created_at': record.created_at.strftime('%Y-%m-%d %H:%M'),
    }
    
    photos = []
    if record.scanned_barcode_image:
        photos.append({
            'url': record.scanned_barcode_image.url,
            'label': 'Scanned Barcode Image'
        })
    if record.operator_job_card_image:
        photos.append({
            'url': record.operator_job_card_image.url,
            'label': 'Operator Job Card'
        })
    data['photos'] = photos
    
    return JsonResponse(data)

# ==============================================================================
# PWA API ENDPOINTS
# ==============================================================================

@csrf_exempt
def api_submit_offline_data(request):
    """API endpoint to submit offline-synced data"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    try:
        data = json.loads(request.body)
        queue_type = data.get('type')
        record_data = data.get('data')
        
        # Process based on queue type
        if queue_type == 'workinfo':
            record_id = record_data.pop('id', None)
            if record_id:
                record = IPQCWorkInfo.objects.get(id=record_id)
                for key, value in record_data.items():
                    setattr(record, key, value)
                record.save()
            else:
                IPQCWorkInfo.objects.create(**record_data)
                
        elif queue_type == 'assembly_audit':
            record_id = record_data.pop('id', None)
            if record_id:
                record = IPQCAssemblyAudit.objects.get(id=record_id)
                for key, value in record_data.items():
                    setattr(record, key, value)
                record.save()
            else:
                IPQCAssemblyAudit.objects.create(**record_data)
                
        elif queue_type == 'fai_inspection':
            record_id = record_data.pop('id', None)
            if record_id:
                record = TestingFirstArticleInspection.objects.get(id=record_id)
                for key, value in record_data.items():
                    setattr(record, key, value)
                record.save()
            else:
                TestingFirstArticleInspection.objects.create(**record_data)
                
        # Add other queue types as needed...
        
        return JsonResponse({'success': True, 'message': 'Data synced successfully'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def api_get_form_data(request):
    """API endpoint to get form data for offline forms"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    form_type = request.GET.get('form_type')
    
    try:
        if form_type == 'work_info':
            form_data = {
                'fields': [
                    {'name': 'date', 'type': 'date', 'required': True},
                    {'name': 'shift', 'type': 'select', 'required': True, 'options': ['Day', 'Night']},
                    {'name': 'line', 'type': 'text', 'required': True},
                    {'name': 'group', 'type': 'text', 'required': True},
                    {'name': 'model', 'type': 'text', 'required': True},
                    {'name': 'color', 'type': 'text', 'required': True},
                ]
            }
        elif form_type == 'assembly_audit':
            form_data = {
                'fields': [
                    {'name': 'date', 'type': 'date', 'required': True},
                    {'name': 'shift', 'type': 'select', 'required': True, 'options': ['Day', 'Night']},
                    {'name': 'line', 'type': 'text', 'required': True},
                    {'name': 'group', 'type': 'text', 'required': True},
                    {'name': 'model', 'type': 'text', 'required': True},
                    {'name': 'color', 'type': 'text', 'required': True},
                    # Add all other fields...
                ]
            }
        elif form_type == 'fai_inspection':
            form_data = {
                'fields': [
                    {'name': 'date', 'type': 'date', 'required': True},
                    {'name': 'shift', 'type': 'select', 'required': True, 'options': ['Day', 'Night']},
                    {'name': 'line', 'type': 'text', 'required': True},
                    {'name': 'group', 'type': 'text', 'required': True},
                    {'name': 'model', 'type': 'text', 'required': True},
                    {'name': 'color', 'type': 'text', 'required': True},
                    # Add all other fields...
                ]
            }
        else:
            return JsonResponse({'error': 'Invalid form type'}, status=400)
            
        return JsonResponse(form_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    
    
    
    



def work_info_success(request):
    """Success page for work info form submission"""
    return render(request, 'ipqc/success/work_info_success.html')
 
def dynamic_form_success(request):
    """Success page for dynamic form submission"""
    return render(request, 'ipqc/success/dynamic_form_success.html')
 
def audit_success(request):
    """Success page for assembly audit submission"""
    return render(request, 'ipqc/success/audit_success.html')
 
def btb_checksheet_success(request):
    """Success page for BTB fitment checksheet submission"""
    return render(request, 'ipqc/success/btb_checksheet_success.html')
 
def ass_dummy_test_success(request):
    """Success page for Assy dummy test submission"""
    return render(request, 'ipqc/success/ass_dummy_test_success.html')
 
def disassemble_success(request):
    """Success page for disassemble checklist submission"""
    return render(request, 'ipqc/success/disassemble_success.html')
 
def nc_issue_success(request):
    """Success page for NC issue tracking submission"""
    return render(request, 'ipqc/success/nc_issue_success.html')
 
def esd_success(request):
    """Success page for ESD compliance checklist submission"""
    return render(request, 'ipqc/success/esd_success.html')
 
def dust_count_success(request):
    """Success page for dust count checklist submission"""
    return render(request, 'ipqc/success/dust_count_success.html')
 
def fai_success(request):
    """Success page for FAI submission"""
    return render(request, 'ipqc/success/fai_success.html')
 
def operator_qualification_success(request):
    """Success page for operator qualification submission"""
    return render(request, 'ipqc/success/operator_qualification_success.html')
 
def register_service_worker(request):
    """Register service worker for PWA"""
    return render(request, 'ipqc/success/register_sw.html')