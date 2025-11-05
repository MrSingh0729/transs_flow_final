from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django import forms
import json
from accounts.models import Employee
from .forms import WorkInfoForm, IPQCAssemblyAuditForm, FIELDS_WITH_REMARKS, BTBFitmentChecksheetForm, AssDummyTestForm, IPQCDisassembleCheckListForm, NCIssueTrackingForm, ESDComplianceChecklistForm, DustCountCheckForm, TestingFirstArticleInspectionForm
from .services import write_to_bitable, write_to_bitable_dynamic, date_to_ms
from datetime import timedelta, datetime, date
from .models import IPQCWorkInfo, DynamicForm, DynamicFormField, DynamicFormSubmission, IPQCAssemblyAudit, BTBFitmentChecksheet, AssDummyTest, IPQCDisassembleCheckList, NCIssueTracking, ESDComplianceChecklist, DustCountCheck, TestingFirstArticleInspection
import pandas as pd
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DetailView
from accounts.role_decorator import RoleRequiredMixin, role_required
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, Http404
from django.db import connections
from django.views.decorators.http import require_GET
from django.conf import settings
from django.http import HttpResponse
import os
from django.urls import reverse
 
# ==============================================================================
# EXISTING FUNCTION-BASED VIEWS (UNCHANGED)
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

            success, message = write_to_bitable(work_info)
            if success:
                messages.success(request, 'Work info saved and synced to Lark Bitable!')
            else:
                messages.warning(request, f'Work info saved but failed to sync: {message}')

            return redirect('ipqc_home')
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

    # Calculate time periods
    now = timezone.localtime()
    today = now.date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)

    # Work info check
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

    is_admin = user.is_superuser or getattr(user, 'role', '').lower() == 'admin'
    
    # Set filters for non-admin users - Fix this part
    base_filter = {}
    if not is_admin and emp_id:
        # Use inspector_name field instead of emp_id for FAI records
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

    # FAI counts - Fix this part
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
    }

    return render(request, 'ipqc/home.html', context)
 
@login_required
@role_required(["IPQC", "QA"])
def info_dash(request):
    emp_id = request.user.employee_id  # Use the correct Employee ID field
 
    today = timezone.localdate()  # safer than timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=6)  # Sunday
 
    # Filter data by logged-in employee ID
    today_records = IPQCWorkInfo.objects. filter(date=today, emp_id=emp_id).count()
    week_records = IPQCWorkInfo.objects. filter(
    date__range=[start_of_week, end_of_week],
    emp_id=emp_id
    ).count()
    total_records = IPQCWorkInfo.objects. filter(emp_id=emp_id).count()
    recent_records = IPQCWorkInfo.objects. filter(
    emp_id=emp_id,
    date__range=[start_of_week, end_of_week]  # optional if you only want recent this week
    ).order_by('-created_at')[:5]
 
    context = {
        'first_name': request.user.full_name.split()[0],
        'designation': request.user.role,
        'today_records': today_records,
        'week_records': week_records,
        'total_records': total_records,
        'recent_records': recent_records,
    }
    return render(request, 'ipqc/info_dash.html', context)
 
 
@login_required
@role_required()
def fill_dynamic_form(request, form_id):
    form_obj = get_object_or_404(DynamicForm, id=form_id)
    fields = form_obj.fields. all()
 
    # ---------------- Get today's IPQC Work Info ----------------
    work_info_today = IPQCWorkInfo.objects. filter(
        emp_id=request.user.employee_id,
        date=timezone.localdate()
    ).order_by('-created_at').first()
 
    if not work_info_today:
        messages.warning(request, "Please fill your IPQC Work Info for today before submitting dynamic forms.")
        return redirect('ipqc_work_info')  # redirect only once here
 
    # ---------------- Pre-fill Work Info Data ----------------
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
 
    # ---------------- Build Dynamic Form ----------------
    CustomForm = type('CustomForm', (forms. Form,), {})
 
    # Add prefilled IPQC fields
    for key, value in prefill_work_info.items():
        if key == 'Date':
            CustomForm.base_fields[key] = forms. DateField(
                initial=value,
            widget=forms. DateInput(attrs={'type': 'date'}),
                required=True
            )
        else:
            CustomForm.base_fields[key] = forms. CharField(initial=value, required=True)
 
    # Add dynamic form fields
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
 
    # ---------------- Handle Submission ----------------
    if request.method == 'POST':
        form = CustomForm(request. POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
 
            # Dynamic form submission
            dynamic_data = {k: v for k, v in cleaned_data.items() if k not in prefill_work_info}
            submission = DynamicFormSubmission.objects.create(
                form=form_obj,
                submitted_by=request.user,
                data=dynamic_data
            )
 
            # IPQC Work Info (already exists, just update if changed)
            ipqc_data = {k: v for k, v in cleaned_data.items() if k in prefill_work_info}
            for field, value in ipqc_data.items():
                setattr(work_info_today, field.lower(), value)
            work_info_today.save()
 
            # Combine both and send to Lark
            combined_data = {**ipqc_data, **dynamic_data}
            if 'Date' in combined_data and isinstance(combined_data['Date'], (datetime, date)):
                combined_data['Date'] = date_to_ms(combined_data['Date'])
 
            success, message = write_to_bitable_dynamic(form_obj.lark_bitable_table_id, combined_data)
            messages.success(
                request,
                f"Form submitted! {message if success else 'Saved locally to MySQL.'}"
            )
            return redirect('ipqc_home')
    else:
        form = CustomForm()
 
    return render(request, 'ipqc/dynamic_form.html', {
        'form': form,
        'form_obj': form_obj,
        'work_info_today': work_info_today
    })
 
 
@login_required
@role_required()
def create_dynamic_form(request):
    if request.method == "POST":
        title = request. POST.get("title").strip()
        description = request. POST.get("description")
        lark_bitable_table_id = request. POST.get("lark_bitable_table_id")
        fields_data = request. POST.get("fields_data") # JSON string
 
        # Check if title already exists
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
 
    return render(request, "ipqc/create_dynamic_form.html")
 
 
@login_required
@role_required()
def dynamic_form_dashboard(request, form_id):
    form_obj = get_object_or_404(DynamicForm, id=form_id)
    submissions = DynamicFormSubmission.objects. filter(form=form_obj)
 
    # Convert to DataFrame for analysis (optional)
    df = pd. DataFrame([s.data for s in submissions])
    df['submitted_by'] = [s.submitted_by.full_name for s in submissions]
    df['created_at'] = [s.created_at for s in submissions]
 
    # Example metrics
    total_submissions = len(df)
    latest_submission = df['created_at']. max() if  not df.empty else  None
 
    # Example field-level stats (only for numeric fields)
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
        "data_json": df.to_json(orient='records') if not df.empty else '[]'
    }
 
    return render(request, "ipqc/dynamic_dashboard.html", context)
 
 
# ==============================================================================
# IPQC ASSEMBLY AUDIT VIEWS (NEW & UPDATED)
# ==============================================================================
 
# --- Mixin to define permission test for editing/deleting ---
class UserCanEditAuditMixin(UserPassesTestMixin):
    def test_func(self):
        """Check if the user is an admin or the owner of the audit."""
        audit = self.get_object()
        user = self.request.user
        if user.is_superuser or user.role.lower() == 'admin':
            return True
        # Check ownership by comparing emp_id
        return audit.emp_id == user.employee_id
 
 
# --- LIST VIEW ---
class IPQCAssemblyAuditListView(RoleRequiredMixin, LoginRequiredMixin, ListView):
    allowed_roles = ["IPQC"]
    model = IPQCAssemblyAudit
    template_name = 'ipqc/audit_list.html'
    context_object_name = 'audits'  # Name for the list in the template
    paginate_by = 10  # Optional: for pagination
 
    def get_queryset(self):
        """Filter records based on user role and employee_id."""
        user = self.request.user
        if user.is_superuser or user.role.lower() == 'admin':
            return IPQCAssemblyAudit.objects. all()
        else:
            return IPQCAssemblyAudit.objects. filter(emp_id=user.employee_id)
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin'] = self.request.user.is_superuser or self.request.user.role.lower() == 'admin'
        return context
 
 
# --- CREATE VIEW (UPDATED) ---
class IPQCAssemblyAuditCreateView(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    allowed_roles = ["IPQC"]
    model = IPQCAssemblyAudit
    form_class = IPQCAssemblyAuditForm
    template_name = 'ipqc/ipqc_assembly_audit_form.html'
    success_url = reverse_lazy('ipqc_audit_list') # Redirect to list page after creation
 
    def get_initial(self):
        initial = super().get_initial()
        emp_id = getattr(self.request.user, 'employee_id', None)
 
        # Pre-fill PQE/TL signature with logged-in user's name
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
        
        # Each item is a tuple: (main_field, remark_field)
        context['man_fields'] = [(form['man_job_card'], form['remark_man_job_card']), (form['man_btb_mon'], form['remark_man_btb_mon'])]
        context['machine_fields'] = [
            (form['mach_epa_check'], form['remark_mach_epa_check']), (form['mach_screw_torque'], form['remark_mach_screw_torque']),
            (form['mach_light'], form['remark_mach_light']), (form['mach_fixture_clean'], form['remark_mach_fixture_clean']),
            (form['mach_jig_label'], form['remark_mach_jig_label']), (form['mach_teflon'], form['remark_mach_teflon']),
            (form['mach_press_params'], form['remark_mach_press_params']), (form['mach_glue_params'], form['remark_mach_glue_params']),
            (form['mach_eq_move_notify'], form['remark_mach_eq_move_notify']), (form['mach_feeler_gauge'], form['remark_mach_feeler_gauge']),
            (form['mach_hot_cold_press'], form['remark_mach_hot_cold_press']), (form['mach_ion_fan'], form['remark_mach_ion_fan']),
            (form['mach_cleanroom_eq'], form['remark_mach_cleanroom_eq']), (form['mach_rti_check'], form['remark_mach_rti_check']),
            (form['mach_current_test'], form['remark_mach_current_test']), (form['mach_pal_qr'], form['remark_mach_pal_qr']),
            (form['mach_auto_screw'], form['remark_mach_auto_screw']),
        ]
        context['material_fields'] = [
            (form['mat_key_check'], form['remark_mat_key_check']), (form['mat_special_stop'], form['remark_mat_special_stop']),
            (form['mat_improved_monitor'], form['remark_mat_improved_monitor']), (form['mat_result_check'], form['remark_mat_result_check']),
            (form['mat_battery_issue'], form['remark_mat_battery_issue']), (form['mat_ipa_check'], form['remark_mat_ipa_check']),
            (form['mat_thermal_gel'], form['remark_mat_thermal_gel']), (form['mat_verification'], form['remark_mat_verification']),
        ]
        context['method_fields'] = [
            (form['meth_sop_seq'], form['remark_meth_sop_seq']), (form['meth_distance_sensor'], form['remark_meth_distance_sensor']),
            (form['meth_rear_camera'], form['remark_meth_rear_camera']), (form['meth_material_handling'], form['remark_meth_material_handling']),
            (form['meth_guideline_doc'], form['remark_meth_guideline_doc']), (form['meth_operation_doc'], form['remark_meth_operation_doc']),
            (form['meth_defective_feedback'], form['remark_meth_defective_feedback']), (form['meth_line_record'], form['remark_meth_line_record']),
            (form['meth_no_self_repair'], form['remark_meth_no_self_repair']), (form['meth_battery_fix'], form['remark_meth_battery_fix']),
            (form['meth_line_change'], form['remark_meth_line_change']), (form['meth_trail_run'], form['remark_meth_trail_run']),
            (form['meth_dummy_conduct'], form['remark_meth_dummy_conduct']),
        ]
        context['environment_fields'] = [(form['env_prod_monitor'], form['remark_env_prod_monitor']), (form['env_5s'], form['remark_env_5s'])]
        context['trc_fields'] = [
            (form['trc_flow_chart'], form['remark_trc_flow_chart']), (form['fai_check'], form['remark_fai_check']),
            (form['defect_monitor'], form['remark_defect_monitor']), (form['spot_check'], form['remark_spot_check']),
            (form['auto_screw_sample'], form['remark_auto_screw_sample']),
        ]
        return context
 
    def form_valid(self, form):
        # --- KEY CHANGE: Assign employee_id and name from the logged-in user ---
        form.instance.emp_id = self.request.user.employee_id
        form.instance.name = self.request.user.full_name
 
        # --- Aggregate Remarks ---
        aggregated_remarks = []
        for field_name in FIELDS_WITH_REMARKS:
            remark_key = f'remark_{field_name}'
            remark_text = self.request.POST.get(remark_key, '').strip()
            if remark_text:
                verbose_name = form.fields[field_name].label
                aggregated_remarks.append(f"{verbose_name}: {remark_text}")
        
        main_remark = self.request.POST.get('remarks', '').strip()
        final_remarks = "\n".join(aggregated_remarks)
        if main_remark:
            final_remarks += f"\n\nGeneral Remarks:\n{main_remark}"
        
        form.instance.remarks = final_remarks
        
        messages.success(self.request, "Audit record created successfully!")
        return super().form_valid(form)
 
 
# --- UPDATE VIEW ---
class IPQCAssemblyAuditUpdateView(RoleRequiredMixin, LoginRequiredMixin, UserCanEditAuditMixin, UpdateView):
    allowed_roles = ["IPQC"]
    model = IPQCAssemblyAudit
    form_class = IPQCAssemblyAuditForm
    template_name = 'ipqc/ipqc_assembly_audit_update_form.html'
    success_url = reverse_lazy('ipqc_audit_list')
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True
        # Re-use the same context preparation as the create view
        form = context['form']
        context['man_fields'] = [(form['man_job_card'], form['remark_man_job_card']), (form['man_btb_mon'], form['remark_man_btb_mon'])]
        # ... (add all other field lists here, same as in CreateView) ...
        context['machine_fields'] = [
            (form['mach_epa_check'], form['remark_mach_epa_check']), (form['mach_screw_torque'], form['remark_mach_screw_torque']),
            (form['mach_light'], form['remark_mach_light']), (form['mach_fixture_clean'], form['remark_mach_fixture_clean']),
            (form['mach_jig_label'], form['remark_mach_jig_label']), (form['mach_teflon'], form['remark_mach_teflon']),
            (form['mach_press_params'], form['remark_mach_press_params']), (form['mach_glue_params'], form['remark_mach_glue_params']),
            (form['mach_eq_move_notify'], form['remark_mach_eq_move_notify']), (form['mach_feeler_gauge'], form['remark_mach_feeler_gauge']),
            (form['mach_hot_cold_press'], form['remark_mach_hot_cold_press']), (form['mach_ion_fan'], form['remark_mach_ion_fan']),
            (form['mach_cleanroom_eq'], form['remark_mach_cleanroom_eq']), (form['mach_rti_check'], form['remark_mach_rti_check']),
            (form['mach_current_test'], form['remark_mach_current_test']), (form['mach_pal_qr'], form['remark_mach_pal_qr']),
            (form['mach_auto_screw'], form['remark_mach_auto_screw']),
        ]
        context['material_fields'] = [
            (form['mat_key_check'], form['remark_mat_key_check']), (form['mat_special_stop'], form['remark_mat_special_stop']),
            (form['mat_improved_monitor'], form['remark_mat_improved_monitor']), (form['mat_result_check'], form['remark_mat_result_check']),
            (form['mat_battery_issue'], form['remark_mat_battery_issue']), (form['mat_ipa_check'], form['remark_mat_ipa_check']),
            (form['mat_thermal_gel'], form['remark_mat_thermal_gel']), (form['mat_verification'], form['remark_mat_verification']),
        ]
        context['method_fields'] = [
            (form['meth_sop_seq'], form['remark_meth_sop_seq']), (form['meth_distance_sensor'], form['remark_meth_distance_sensor']),
            (form['meth_rear_camera'], form['remark_meth_rear_camera']), (form['meth_material_handling'], form['remark_meth_material_handling']),
            (form['meth_guideline_doc'], form['remark_meth_guideline_doc']), (form['meth_operation_doc'], form['remark_meth_operation_doc']),
            (form['meth_defective_feedback'], form['remark_meth_defective_feedback']), (form['meth_line_record'], form['remark_meth_line_record']),
            (form['meth_no_self_repair'], form['remark_meth_no_self_repair']), (form['meth_battery_fix'], form['remark_meth_battery_fix']),
            (form['meth_line_change'], form['remark_meth_line_change']), (form['meth_trail_run'], form['remark_meth_trail_run']),
            (form['meth_dummy_conduct'], form['remark_meth_dummy_conduct']),
        ]
        context['environment_fields'] = [(form['env_prod_monitor'], form['remark_env_prod_monitor']), (form['env_5s'], form['remark_env_5s'])]
        context['trc_fields'] = [
            (form['trc_flow_chart'], form['remark_trc_flow_chart']), (form['fai_check'], form['remark_fai_check']),
            (form['defect_monitor'], form['remark_defect_monitor']), (form['spot_check'], form['remark_spot_check']),
            (form['auto_screw_sample'], form['remark_auto_screw_sample']),
        ]
        return context
 
    def form_valid(self, form):
        # --- Aggregate Remarks (same logic as CreateView) ---
        aggregated_remarks = []
        for field_name in FIELDS_WITH_REMARKS:
            remark_key = f'remark_{field_name}'
            remark_text = self.request.POST.get(remark_key, '').strip()
            if remark_text:
                verbose_name = form.fields[field_name].label
                aggregated_remarks.append(f"{verbose_name}: {remark_text}")
        
        main_remark = self.request.POST.get('remarks', '').strip()
        final_remarks = "\n".join(aggregated_remarks)
        if main_remark:
            final_remarks += f"\n\nGeneral Remarks:\n{main_remark}"
        
        form.instance.remarks = final_remarks
 
        messages.success(self.request, "Audit record updated successfully!")
        return super().form_valid(form)
 
 
# --- DELETE VIEW ---
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

    # List of hours to use in template
    HOURS = ['9','10','11','12','1','2','3','4','5','6']

    def get_initial(self):
        initial = super().get_initial()
        emp_id = getattr(self.request.user, 'employee_id', None)
 
        # Pre-fill PQE/TL signature with logged-in user's name
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

    # Pass hours to template context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hours = ['9','10','11','12','1','2','3','4','5','6']
        context['hours'] = hours
        # Prepare a dict of all fields per hour
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
        return context

    def form_valid(self, form):
        # Check user authentication
        if not self.request.user.is_authenticated:
            messages.error(self.request, "You must be logged in to submit this form.")
            return self.form_invalid(form)

        # Ensure the user exists in the database
        try:
            user = self.request.user
            if not user.pk or not user.is_active:
                raise ValueError("Current user is invalid.")
        except Exception:
            messages.error(self.request, "Current user is invalid. Please contact admin.")
            return self.form_invalid(form)

        # Load aggregated data safely
        aggregated_data_json = self.request.POST.get('aggregated_data', '{}')
        try:
            aggregated_data = json.loads(aggregated_data_json)
        except json.JSONDecodeError:
            messages.error(self.request, "There was an error processing the form data. Please try again.")
            return self.form_invalid(form)

        # Set all fields from aggregated_data
        for key, value in aggregated_data.items():
            if hasattr(form.instance, key):
                setattr(form.instance, key, value)

        # Assign the valid user
        form.instance.created_by = user

        messages.success(self.request, "BTB Fitment Checksheet submitted successfully!")
        return super().form_valid(form)

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
        
        
class BTBFitmentChecksheetDetailView(RoleRequiredMixin, LoginRequiredMixin, DetailView):
    allowed_roles = ["IPQC"]
    model = BTBFitmentChecksheet
    template_name = 'ipqc/btb_checksheet_detail.html'
    context_object_name = 'sheet' # This lets you use {{ sheet }} in the template

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # You can add extra context here if needed
        return context
    
class AssyDummyTestCreate(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    allowed_roles = ["IPQC"]
    model = AssDummyTest
    form_class = AssDummyTestForm
    template_name = 'ipqc/ass_dummy_test_form.html'
    success_url = reverse_lazy('ass_dummy_test_list')

    def get_initial(self):
        """Prefill form fields based on logged-in user and latest work info."""
        initial = super().get_initial()
        user = self.request.user

        # Prefill PQE/TL signature
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
        """Process aggregated JSON data and assign the logged-in user."""
        user = self.request.user

        # Safely load aggregated_data JSON from POST
        aggregated_data_json = self.request.POST.get('aggregated_data', '{}')
        try:
            aggregated_data = json.loads(aggregated_data_json)
        except json.JSONDecodeError:
            messages.error(self.request, "Error processing form data. Please try again.")
            return self.form_invalid(form)

        # Safely set fields from aggregated_data, excluding sensitive fields
        sensitive_fields = {'id', 'pk', 'created_by', 'updated_at', 'created_at'}
        for key, value in aggregated_data.items():
            if hasattr(form.instance, key) and key not in sensitive_fields:
                setattr(form.instance, key, value)

        # Assign the logged-in user as creator
        form.instance.created_by = user

        messages.success(self.request, "BTB Fitment Checksheet submitted successfully!")
        return super().form_valid(form)
    
    
class AssDummyTestListView(RoleRequiredMixin, LoginRequiredMixin, ListView):
    allowed_roles = ["IPQC"]            # only IPQC role can access
    model = AssDummyTest
    template_name = 'ipqc/ass_dummy_test_list.html'
    context_object_name = 'tests'       # this is used in the template instead of object_list
    ordering = ['-date', '-id']         # latest records first
    paginate_by = 25                    # optional: pagination
    
    
class IPQCDisassembleCheckListCreateView(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    allowed_roles = ["IPQC"]
    model = IPQCDisassembleCheckList
    form_class = IPQCDisassembleCheckListForm
    template_name = 'ipqc/ipqc_disassemble_form.html'
    success_url = reverse_lazy('ipqc_disassemble_list')

    def get_initial(self):
        """Prefill form fields based on latest work info for logged-in user."""
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
        """Handle form submission successfully."""
        # Track who submitted (if model supports it)
        if hasattr(form.instance, 'created_by'):
            form.instance.created_by = self.request.user

        messages.success(self.request, "✅ IPQC Disassemble Checklist submitted successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        """Custom invalid form handler with clearer error reporting."""
        messages.error(self.request, "❌ Please correct the highlighted errors before submitting.")
        return super().form_invalid(form)

class IPQCDisassembleCheckListView(RoleRequiredMixin, LoginRequiredMixin, ListView):
    allowed_roles = ["IPQC"]
    model = IPQCDisassembleCheckList
    template_name = 'ipqc/ipqc_disassemble_list.html'
    context_object_name = 'records'
    paginate_by = 20  # Show 20 records per page

    def get_queryset(self):
        """Enable search and filtering by multiple parameters."""
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
        """
        Calculate overall status based on all checkpoint fields
        Returns: 'PASS', 'FAIL', or 'MIXED'
        """
        # Get all choice fields (skip non-choice fields)
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
        """Add statistics for dashboard display."""
        context = super().get_context_data(**kwargs)
        
        # Calculate statistics
        from django.utils import timezone
        from datetime import timedelta
        import datetime
        
        today = timezone.now().date()
        week_start = today - datetime.timedelta(days=today.weekday())
        
        # Get all records
        all_records = self.model.objects.all()
        
        # Calculate statistics
        stats = {
            'today': all_records.filter(created_at__date=today).count(),
            'week': all_records.filter(created_at__date__gte=week_start).count(),
            'total': all_records.count(),
        }
        
        # Add stats to context
        context['ipqc_disassemble_stats'] = stats
        
        # Additional context for dashboard
        context['total_records'] = stats['total']
        context['recent_submissions'] = self.model.objects.order_by('-created_at')[:5]
        
        return context
    
class IPQCDisassembleDetailView(DetailView):
    model = IPQCDisassembleCheckList
    
    def get(self, request, *args, **kwargs):
        try:
            record = self.get_object()
            
            # Prepare basic info
            data = {
                # Basic Information
                'date': record.date.strftime('%Y-%m-%d'),
                'shift': record.shift,
                'emp_id': record.emp_id,
                'name': record.name,
                'section': record.section,
                'line': record.line,
                'group': record.group,
                'model': record.model,
                'color': record.color,
                
                # Appearance / Assembly Quality
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
                
                # Assembly as per SOP
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
                
                # Component & Connection Check
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
                
                # Glue / Fixture Validation
                'jig_fixture_test': record.jig_fixture_test,
                'glue_location': record.glue_location,
                'glue_weight_1': str(record.glue_weight_1) if record.glue_weight_1 else None,
                'glue_weight_2': str(record.glue_weight_2) if record.glue_weight_2 else None,
                'glue_weight_3': str(record.glue_weight_3) if record.glue_weight_3 else None,
                
                # Final fields
                'defect_cause': record.defect_cause,
                'imei1': record.imei1,
                'imei2': record.imei2,
                'pqe': record.pqe,
                'pe': record.pe,
                'apd_ll': record.apd_ll,
                'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                
                # Photos array
                'photos': []
            }
            
            # Add photo URLs
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
            # Log the error for debugging
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

    def get_initial(self):
        """Prefill form fields based on logged-in user and latest work info."""
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
        """Handle form submission and save safely."""
        user = self.request.user

        # Safely load aggregated data JSON (if sent from frontend)
        aggregated_data_json = self.request.POST.get('aggregated_data', '{}')
        try:
            aggregated_data = json.loads(aggregated_data_json)
        except json.JSONDecodeError:
            messages.error(self.request, "Error processing form data. Please try again.")
            return self.form_invalid(form)

        # Avoid overwriting sensitive fields
        sensitive_fields = {'id', 'pk', 'created_at', 'updated_at'}
        for key, value in aggregated_data.items():
            if hasattr(form.instance, key) and key not in sensitive_fields:
                setattr(form.instance, key, value)

        # Optionally track who created the record (if field exists)
        if hasattr(form.instance, 'created_by'):
            form.instance.created_by = user

        messages.success(self.request, "✅ IPQC Disassemble Checklist submitted successfully!")
        return super().form_valid(form)
    
    
class NCIssueTrackingListView(RoleRequiredMixin, LoginRequiredMixin, ListView):
    allowed_roles = ["IPQC"]
    model = NCIssueTracking
    template_name = 'ipqc/nc_issue_tracking_list.html'
    context_object_name = 'records'
    paginate_by = 20  # show 20 per page

    def get_queryset(self):
        """Optional search and filter by date, model, or employee."""
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
    
class ESDComplianceChecklistCreateView(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    allowed_roles = ["IPQC"]
    model = ESDComplianceChecklist
    form_class = ESDComplianceChecklistForm
    template_name = 'ipqc/esd_compliance_checklist_form.html'
    success_url = reverse_lazy('esd_compliance_checklist_list')

    def get_initial(self):
        """Prefill form fields based on logged-in user and latest work info."""
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
        """Save form normally and attach creator info if applicable."""
        if hasattr(form.instance, 'created_by'):
            form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "✅ ESD Compliance Checklist submitted successfully!")
        return response

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
        # Call the base implementation first to get the existing context
        context = super().get_context_data(**kwargs)
        
        # We use the base model's queryset for stats, so search doesn't affect the counts
        base_queryset = self.model.objects.all()
        
        # Get today's date
        today = timezone.now().date()
        
        # Calculate statistics
        context['total_records'] = base_queryset.count()
        context['today_records'] = base_queryset.filter(date=today).count()
        
        # Calculate the start of the current week (Monday is day 0)
        start_of_week = today - timedelta(days=today.weekday())
        context['week_records'] = base_queryset.filter(date__gte=start_of_week).count()
        
        # The updated context is returned automatically
        return context

@require_GET
def esd_compliance_checklist_details(request, pk):
    """AJAX endpoint to fetch ESD checklist details in a structured format."""
    record = get_object_or_404(ESDComplianceChecklist, pk=pk)
    
    def get_verbose_name(field_name):
        try:
            return record._meta.get_field(field_name).verbose_name
        except:
            return field_name.replace('_', ' ').title()

    # --- Basic Info ---
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

    # --- ROBUST MODIFICATION ---
    # Try to get the status, but don't crash if the method is missing.
    overall_status = 'N/A'
    if hasattr(record, 'get_overall_status'):
        overall_status = record.get_overall_status()
    # --- END OF MODIFICATION ---

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

    def get_initial(self):
        """Prefill form fields based on logged-in user and latest work info."""
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
        """Save the form normally and set created_by if needed."""
        if hasattr(form.instance, 'created_by'):
            form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "✅ ESD Compliance Checklist submitted successfully!")
        return response

class DustCountListView(ListView):
    model = DustCountCheck
    template_name = 'ipqc/dust_count_checklist_list.html'
    context_object_name = 'records'
    paginate_by = 10  # optional, for pagination

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
    
class TestingFirstArticleInspectionCreateView(LoginRequiredMixin, CreateView):
    model = TestingFirstArticleInspection
    form_class = TestingFirstArticleInspectionForm
    template_name = 'ipqc/testing_fai_form.html'
    success_url = reverse_lazy('testing_fai_list')
    
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
        instance = self. object  # Get the saved record
        public_link = self.request.build_absolute_uri(reverse('testing_fai_public_update', args=[str(instance.public_token)]))
        instance.public_url = public_link
        instance.save(update_fields=['public_url'])
        messages.success(self.request, f"✅ Record created! QE link generated.")
        return response
    
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
        
        # Add statistics - call get_queryset() without arguments to respect permissions
        queryset_for_stats = self.get_queryset()
        
        # Add statistics
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
        return context
 
def download_testing_fai_evidence(request, pk, evidence_type):
    """Download an evidence file, checking for permissions."""
    fai = get_object_or_404(TestingFirstArticleInspection, pk=pk)
    if not (request.user.is_superuser or 
 request.user.groups. filter(name__in=['Admin', 'QA']).exists() or
            fai.inspector_name == (request.user.full_name() or request.user.username)):
        raise Http404("Permission denied.")
 
    evidence_fields = {
        'label_photo': fai.label_check_evidence, 'label_position_photo': fai.label_position_check_evidence,
        'logo_photo': fai.logo_check_evidence, 'assembly_photo': fai.assembly_battery_check_evidence,
        'boot_video': fai.boot_time_test_evidence, 'cam_front_photo': fai.camera_front_test_evidence,
        'cam_back_photo': fai.camera_back_test_evidence, 'cam_dark_photo': fai.camera_dark_test_evidence,
        'temp_cam_photo': fai.high_temp_camera_test_evidence, 'imei_photo': fai.imei_photo,
    }
    file = evidence_fields.get(evidence_type)
    if not file or not file.name:
        raise Http404("Evidence file not found.")
    
    response = HttpResponse(file.read(), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file.name)}"'
    return response
 

def testing_fai_public_qe_update_view(request, public_token):
    """Public form for QE to fill name and approval status"""
    fai_record = get_object_or_404(TestingFirstArticleInspection, public_token=public_token)
    if request.method == "POST":
        qe_name = request. POST.get("qe_confirm_name")
        qe_status = request. POST.get("qe_confirm_status")
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
    """Returns FAI record details as JSON for the modal."""
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
        # Add all check results dynamically
        for field in obj._meta.fields:
            if field.name.endswith(('_check', '_test')) and field.choices:
                data[field.name] = getattr(obj, field.name)
        
        # Add evidence photos
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