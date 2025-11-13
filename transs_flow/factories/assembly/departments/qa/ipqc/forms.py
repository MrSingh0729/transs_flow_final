from django import forms
from django.db import models 
from .models import IPQCWorkInfo, DynamicForm, DynamicFormField, IPQCAssemblyAudit, BTBFitmentChecksheet, AssDummyTest, IPQCDisassembleCheckList, NCIssueTracking, ESDComplianceChecklist, DustCountCheck, TestingFirstArticleInspection, OperatorQualificationCheck, FORM_CHOICES, FORM_APPROVAL, FAI_SITUATION_CHOICES, FORM_RESULT_CHOICES
from django.db import connections
from django.utils import timezone
import mimetypes



class WorkInfoForm(forms.ModelForm):
    class Meta:
        model = IPQCWorkInfo
        fields = ['date', 'shift', 'section', 'line', 'group', 'model', 'color']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full p-2 border rounded'}),
            'shift': forms.Select(choices=[('A', 'A'), ('B', 'B'), ('C', 'C')], attrs={'class': 'w-full p-2 border rounded'}),
            'section': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'line': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'group': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'model': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'color': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
        }

# class WorkInfoForm(forms.ModelForm):
#     class Meta:
#         model = IPQCWorkInfo
#         fields = ['date', 'shift', 'section', 'line', 'group', 'model', 'color', 'status']
#         widgets = {
#             'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#             'shift': forms.Select(choices=IPQCWorkInfo.SHIFT_CHOICES, attrs={'class': 'form-control'}),
#             'section': forms.TextInput(attrs={'class': 'form-control'}),
#             'line': forms.TextInput(attrs={'class': 'form-control'}),
#             'group': forms.TextInput(attrs={'class': 'form-control'}),
#             'model': forms.TextInput(attrs={'class': 'form-control'}),
#             'color': forms.TextInput(attrs={'class': 'form-control'}),
#             'status': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
#         }
        


def get_model_choices():
    """Fetch model names dynamically from defaultdb.model_description"""
    try:
        with connections['defaultdb'].cursor() as cursor:
            cursor.execute("SELECT model_name FROM model_description ORDER BY model_name ASC;")
            rows = cursor.fetchall()
        return [(r[0], r[0]) for r in rows]  # (value, label)
    except Exception:
        return []

LINE_CHOICES = [(f"L{i}", f"L{i}") for i in range(1, 16)]
GROUP_CHOICES = [(f"A{i}", f"A{i}") for i in range(1, 16)]

class WorkInfoForm(forms.ModelForm):
    model = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control select2', 'placeholder': 'Search Model'}),
        required=True
    )
    line = forms.ChoiceField(
        choices=LINE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    group = forms.ChoiceField(
        choices=GROUP_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = IPQCWorkInfo
        fields = ['date', 'shift', 'section', 'line', 'group', 'model', 'color']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'shift': forms.Select(choices=IPQCWorkInfo.SHIFT_CHOICES, attrs={'class': 'form-control'}),
            'section': forms.Select(attrs={'class': 'form-control'}, choices=IPQCWorkInfo.SECTION_CHOICES),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # dynamically load model list every time form is rendered
        self.fields['model'].choices = get_model_choices()


class DynamicFormCreateForm(forms.ModelForm):
    class Meta:
        model = DynamicForm
        fields = ['title', 'description', 'lark_bitable_table_id']

class DynamicFormFieldForm(forms.ModelForm):
    class Meta:
        model = DynamicFormField
        fields = ['label', 'field_type', 'required', 'options', 'order']
        
        
# List of fields that require the special UI with a remark button
FIELDS_WITH_REMARKS = [
    'mach_epa_check', 'mach_screw_torque', 'mach_sholdering_temp',
    'mach_light', 'mach_fixture_clean', 'mach_jig_label', 'mach_teflon',
    'mach_press_params', 'mach_glue_params', 'mach_eq_move_notify',
    'mach_feeler_gauge', 'mach_hot_cold_press', 'mach_ion_fan',
    'mach_cleanroom_eq', 'mach_rti_check', 'mach_current_test', 'mach_pal_qr',
    'mach_auto_screw', 'mat_key_check', 'mat_special_stop', 'mat_improved_monitor',
    'mat_result_check', 'mat_battery_issue', 'mat_ipa_check', 'mat_thermal_gel',
    'mat_verification', 'meth_sop_seq', 'meth_distance_sensor', 'meth_rear_camera',
    'meth_material_handling', 'meth_guideline_doc', 'meth_operation_doc',
    'meth_defective_feedback', 'meth_line_record', 'meth_no_self_repair',
    'meth_battery_fix', 'meth_line_change', 'meth_trail_run', 'meth_dummy_conduct',
    'env_prod_monitor', 'env_5s', 'trc_flow_chart', 'fai_check',
    'defect_monitor', 'spot_check', 'auto_screw_sample'
]
 
class  IPQCAssemblyAuditForm(forms. ModelForm):
    class Meta:
        model = IPQCAssemblyAudit
        fields = '__all__'
        exclude = ['created_at']
        widgets = {
            'remarks': forms. Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'wo_input_qty': forms. NumberInput(attrs={'class': 'form-control'}),
        }
 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Dynamically add remark fields
        for field_name in FIELDS_WITH_REMARKS:
            self.fields[f'remark_{field_name}'] = forms. CharField(
            label=f"Remark for {self.fields[field_name].label}",
            required=False,
            widget=forms. Textarea(attrs={'rows': 2, 'class': 'form-control'})
            )
 
        # Add 'form-control' class and set readonly fields
        readonly_fields = [
            'date', 'shift', 'emp_id', 'name', 'section', 
            'line', 'group', 'model', 'color', 'pqe_tl_sign'
        ]
 
        for field_name, field in self.fields.items():
            if  not  isinstance(field.widget, forms. CheckboxInput):
                field.widget.attrs['class'] = 'form-control'
            
            if field_name in readonly_fields:
                field.widget.attrs['readonly'] = True
                
                
 
class BTBFitmentChecksheetForm(forms.ModelForm):
    class Meta:
        model = BTBFitmentChecksheet
        exclude = ['created_by', 'created_at', 
                   'input_total', 'cam_btb_total', 'lcd_fitment_total', 'main_fpc_total', 'battery_total', 'finger_printer_total',
                   'total_9', 'total_10', 'total_11', 'total_12', 'total_1', 'total_2', 'total_3', 'total_4', 'total_5', 'total_6',
                   'grand_total']
        
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'shift': forms.DateInput(attrs={'type': 'shift', 'class': 'form-control'}),
            'emp_id': forms.DateInput(attrs={'type': 'emp_id', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'line': forms.TextInput(attrs={'class': 'line','class':  'form-control'}),
            'group': forms.TextInput(attrs={'class': 'group','class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'model','class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'color','class': 'form-control'}),
            'frequency': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # --- Logic to make auto-populated fields read-only ---
        auto_populated_fields = ['date', 'shift', 'emp_id', 'name', 'line', 'group', 'model', 'color']
        for field_name in auto_populated_fields:
            if self.initial.get(field_name):
                field = self.fields.get(field_name)
                if field:
                    field.widget.attrs['readonly'] = True
                    field.widget.attrs['class'] += ' bg-light'
        
        # --- Logic for other field types ---
        for field_name, field in self.fields.items():
            if isinstance(field, forms.IntegerField):
                field.widget = forms.NumberInput(attrs={'class': 'form-control form-control-sm text-center', 'min': '0', 'value': '0'})
            
            # --- UPDATED: Add a custom class to Textarea fields ---
            elif isinstance(field, models.TextField):
                field.widget = forms.Textarea(attrs={
                    'class': 'form-control form-control-sm remark-field', # <-- Custom class added here
                    'rows': '2', 
                    'placeholder': 'Add remark...',
                    # The 'style' attribute has been removed
                })
                
                
class AssDummyTestForm(forms.ModelForm):
    class Meta:
        model = AssDummyTest
        fields = [
            'date', 'shift', 'emp_id', 'name', 'area', 'section', 'line', 'group',
            'model', 'color', 'test_stage', 'test_item',
            'operator_name', 'operator_id', 'result', 'cause', 'measure',
            'll_confirm', 'remark'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control'}),
            'shift': forms.TextInput(attrs={'class': 'form-control'}),
            'emp_id': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'area': forms.TextInput(attrs={'class': 'form-control'}),
            'section': forms.TextInput(attrs={'class': 'form-control'}),
            'line': forms.TextInput(attrs={'class': 'form-control'}),
            'group': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'test_stage': forms.TextInput(attrs={'class': 'form-control'}),
            'test_item': forms.TextInput(attrs={'class': 'form-control'}),
            'operator_name': forms.TextInput(attrs={'class': 'form-control'}),
            'operator_id': forms.TextInput(attrs={'class': 'form-control'}),
            'result': forms.Select(attrs={'class': 'form-control'}),
            'cause': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'measure': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'll_confirm': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        
        
class IPQCDisassembleCheckListForm(forms.ModelForm):
    class Meta:
        model = IPQCDisassembleCheckList
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # --- Make work info fields readonly ---
        readonly_fields = [
            'date', 'shift', 'emp_id', 'name',
            'section', 'line', 'group', 'model', 'color'
        ]
        for field_name in readonly_fields:
            self.fields[field_name].widget.attrs['readonly'] = True
            self.fields[field_name].widget.attrs['class'] = 'form-control-plaintext'

        # --- Add styling to all dropdowns and inputs ---
        for field_name, field in self.fields.items():
            if field_name not in readonly_fields:
                if isinstance(field.widget, forms.Select):
                    field.widget.attrs.update({'class': 'form-select'})
                elif isinstance(field.widget, forms.FileInput):
                    field.widget.attrs.update({'class': 'form-control', 'accept': 'image/*'})
                else:
                    field.widget.attrs.update({'class': 'form-control'})

        # --- Add placeholders for text fields ---
        self.fields['defect_cause'].widget.attrs['placeholder'] = "Describe cause of defect (if any)..."
        self.fields['pqe'].widget.attrs['placeholder'] = "Enter PQE name"
        self.fields['pe'].widget.attrs['placeholder'] = "Enter PE name"
        self.fields['apd_ll'].widget.attrs['placeholder'] = "Enter APD LL name"

    def clean(self):
        """
        Custom validation:
        - If any 'Not OK' field is selected, require supporting image proof or remarks.
        """
        cleaned_data = super().clean()
        
        # Get all image fields from the model
        image_fields = [
            'color_match_photo', 'cam_lens_photo', 'key_photo', 
            'screw_photo', 'housing_photo', 'proof_label_photo',
            'assembly_overview_photo', 'defect_photo'
        ]

        # Check if any field marked as "Not OK"
        not_ok_fields = []
        for field_name, value in cleaned_data.items():
            if isinstance(value, str) and value == 'Not OK':
                not_ok_fields.append(field_name)

        # If 'Not OK' found, require at least one image or remark
        if not_ok_fields:
            has_image = False
            for img_field in image_fields:
                if img_field in cleaned_data and cleaned_data.get(img_field):
                    has_image = True
                    break
            
            remarks = cleaned_data.get('defect_cause')
            if not has_image and not remarks:
                raise forms.ValidationError(
                    "Please provide a defect image or description for all 'Not OK' items."
                )

        return cleaned_data
        
        
class NCIssueTrackingForm(forms.ModelForm):
    class Meta:
        model = NCIssueTracking
        fields = [
            # Work Info
            "date", "shift", "emp_id", "name", "section", "line", "group", "model", "color",
            
            # Issue Tracking
            "stage", "time", "issue", "three_why", "solution",
            "operator_name", "operator_id", "responsible_dept", "responsible_person",
            "close_time", "status", "remark",
        ]
        widgets = {
            # Work Info
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "shift": forms.TextInput(attrs={"class": "form-control"}),
            "emp_id": forms.TextInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "section": forms.TextInput(attrs={"class": "form-control"}),
            "line": forms.TextInput(attrs={"class": "form-control"}),
            "group": forms.TextInput(attrs={"class": "form-control"}),
            "model": forms.TextInput(attrs={"class": "form-control"}),
            "color": forms.TextInput(attrs={"class": "form-control"}),

            # Issue Tracking
            "stage": forms.TextInput(attrs={"class": "form-control"}),

            # Change 'time' to datetime-local to store timestamp easily
            "time": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),

            "issue": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "three_why": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "solution": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "operator_name": forms.TextInput(attrs={"class": "form-control"}),
            "operator_id": forms.TextInput(attrs={"class": "form-control"}),
            "responsible_dept": forms.TextInput(attrs={"class": "form-control"}),
            "responsible_person": forms.TextInput(attrs={"class": "form-control"}),

            # Close Time as datetime-local
            "close_time": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),

            "status": forms.TextInput(attrs={"class": "form-control"}),
            "remark": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }
 
    
class ESDComplianceChecklistForm(forms.ModelForm):
    class Meta:
        model = ESDComplianceChecklist
        # Note: Photo fields are not in the main audit list anymore, but they are still in 'fields'
        fields = [
            # --- Basic Info ---
            'date', 'shift', 'emp_id', 'name', 'line', 'group', 'model', 'color',

            # --- 1. Clothing Rules ---
            'epa_clothes', 'forbid_wear_out', 'no_accessories', 'clothes_clean',
            'collar_cover', 'all_buttons_closed', 'clothes_length', 'watch_expose',
            'hair_cap',

            # --- 2. Wristband and Slipper ---
            'slipper_check', 'wristband_check', 'pre_line_check', 'wrist_touch_skin',

            # --- 3. Handling Rules ---
            'no_touch_pcba', 'alert_plug_out',

            # --- 4. Grounding and Equipment ---
            'trolley_grounding', 'device_grounded', 'grounding_points_tight',
            'ion_fan_distance', 'ion_fan_direction',

            # --- 5. Consumables ---
            'gloves_condition', 'mat_grounded', 'audit_label_valid',

            # --- 6. Material Handling ---
            'esds_box', 'table_no_source',

            # --- 7. Tools & Environment ---
            'tools_audit', 'temp_humidity', 'tray_voltage',
            
            # --- Environmental Readings (Numerical Inputs) ---
            'temperature_value', 'humidity_value', 'tray_voltage_value',

            # --- Photo Fields ---
            'epa_clothes_photo', 'hair_cap_photo', 'wristband_photo', 'trolley_photo',
            'ion_fan_photo', 'mat_photo', 'table_photo', 'photo_overview',

            # --- Remarks ---
            'remark',
        ]
        widgets = {
            # --- Basic Info (Readonly) ---
            'date': forms.DateInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:border-sky-500 focus:outline-none bg-gray-50', 'readonly': True}),
            'shift': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:border-sky-500 focus:outline-none bg-gray-50', 'readonly': True}),
            'emp_id': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:border-sky-500 focus:outline-none bg-gray-50', 'readonly': True}),
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:border-sky-500 focus:outline-none bg-gray-50', 'readonly': True}),
            'line': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:border-sky-500 focus:outline-none bg-gray-50', 'readonly': True}),
            'group': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:border-sky-500 focus:outline-none bg-gray-50', 'readonly': True}),
            'model': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:border-sky-500 focus:outline-none bg-gray-50', 'readonly': True}),
            'color': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:border-sky-500 focus:outline-none bg-gray-50', 'readonly': True}),

            # --- Select Fields (Audit Options) ---
            'epa_clothes': forms.Select(attrs={'class': 'status-select'}),
            'forbid_wear_out': forms.Select(attrs={'class': 'status-select'}),
            'no_accessories': forms.Select(attrs={'class': 'status-select'}),
            'clothes_clean': forms.Select(attrs={'class': 'status-select'}),
            'collar_cover': forms.Select(attrs={'class': 'status-select'}),
            'all_buttons_closed': forms.Select(attrs={'class': 'status-select'}),
            'clothes_length': forms.Select(attrs={'class': 'status-select'}),
            'watch_expose': forms.Select(attrs={'class': 'status-select'}),
            'hair_cap': forms.Select(attrs={'class': 'status-select'}),
            'slipper_check': forms.Select(attrs={'class': 'status-select'}),
            'wristband_check': forms.Select(attrs={'class': 'status-select'}),
            'pre_line_check': forms.Select(attrs={'class': 'status-select'}),
            'wrist_touch_skin': forms.Select(attrs={'class': 'status-select'}),
            'no_touch_pcba': forms.Select(attrs={'class': 'status-select'}),
            'alert_plug_out': forms.Select(attrs={'class': 'status-select'}),
            'trolley_grounding': forms.Select(attrs={'class': 'status-select'}),
            'device_grounded': forms.Select(attrs={'class': 'status-select'}),
            'grounding_points_tight': forms.Select(attrs={'class': 'status-select'}),
            'ion_fan_distance': forms.Select(attrs={'class': 'status-select'}),
            'ion_fan_direction': forms.Select(attrs={'class': 'status-select'}),
            'gloves_condition': forms.Select(attrs={'class': 'status-select'}),
            'mat_grounded': forms.Select(attrs={'class': 'status-select'}),
            'audit_label_valid': forms.Select(attrs={'class': 'status-select'}),
            'esds_box': forms.Select(attrs={'class': 'status-select'}),
            'table_no_source': forms.Select(attrs={'class': 'status-select'}),
            'tools_audit': forms.Select(attrs={'class': 'status-select'}),
            'temp_humidity': forms.Select(attrs={'class': 'status-select'}),
            'tray_voltage': forms.Select(attrs={'class': 'status-select'}),

            # --- Numerical Inputs ---
            'temperature_value': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:border-sky-500 focus:outline-none', 'step': '0.01', 'placeholder': 'e.g., 22.50'}),
            'humidity_value': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:border-sky-500 focus:outline-none', 'step': '0.01', 'placeholder': 'e.g., 45.00'}),
            'tray_voltage_value': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:border-sky-500 focus:outline-none', 'step': '0.01', 'placeholder': 'e.g., -15.50'}),

            # --- Textarea ---
            'remark': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:border-sky-500 focus:outline-none', 'rows': 4, 'placeholder': 'Enter any detailed remarks here...'}),
            
            # --- File Inputs (LIVE CAMERA CAPTURE) ---
            # The 'capture="environment"' attribute tells mobile browsers to open the rear camera.
            'epa_clothes_photo': forms.FileInput(attrs={'accept': 'image/*', 'capture': 'environment', 'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-sky-50 file:text-sky-700 hover:file:bg-sky-100'}),
            'hair_cap_photo': forms.FileInput(attrs={'accept': 'image/*', 'capture': 'environment', 'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-sky-50 file:text-sky-700 hover:file:bg-sky-100'}),
            'wristband_photo': forms.FileInput(attrs={'accept': 'image/*', 'capture': 'environment', 'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-sky-50 file:text-sky-700 hover:file:bg-sky-100'}),
            'trolley_photo': forms.FileInput(attrs={'accept': 'image/*', 'capture': 'environment', 'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-sky-50 file:text-sky-700 hover:file:bg-sky-100'}),
            'ion_fan_photo': forms.FileInput(attrs={'accept': 'image/*', 'capture': 'environment', 'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-sky-50 file:text-sky-700 hover:file:bg-sky-100'}),
            'mat_photo': forms.FileInput(attrs={'accept': 'image/*', 'capture': 'environment', 'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-sky-50 file:text-sky-700 hover:file:bg-sky-100'}),
            'table_photo': forms.FileInput(attrs={'accept': 'image/*', 'capture': 'environment', 'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-sky-50 file:text-sky-700 hover:file:bg-sky-100'}),
            'photo_overview': forms.FileInput(attrs={'accept': 'image/*', 'capture': 'environment', 'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-sky-50 file:text-sky-700 hover:file:bg-sky-100'}),
        }
        
class DustCountCheckForm(forms.ModelForm):
    class Meta:
        model = DustCountCheck
        fields = [
            'date', 'shift', 'emp_id', 'name', 'line', 'group', 'model', 'color',
            'micrometer_0_3', 'micrometer_0_5', 'micrometer_1_0',
            'checked_by', 'verified_by', 'remark'
        ]

        widgets = {
            # --- Basic Info (read-only) ---
            'date': forms.DateInput(attrs={'class': 'form-control', 'readonly': True}),
            'shift': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'emp_id': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'line': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'group': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),

            # --- Particle measurements ---
            'micrometer_0_3': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'micrometer_0_5': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'micrometer_1_0': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),

            # --- Checked & Verified By ---
            'checked_by': forms.TextInput(attrs={'class': 'form-control'}),
            'verified_by': forms.TextInput(attrs={'class': 'form-control'}),

            # --- Remarks ---
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any remarks...'}),
        }
        

class  TestingFirstArticleInspectionForm(forms. ModelForm):
    """Comprehensive FAI form with validation and file handling for the updated model."""
    
    class Meta:
        model = TestingFirstArticleInspection
        fields = '__all__'
        widgets = {
            'date': forms. DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            # 'power_consumption_test': forms. Textarea(attrs={'class': 'form-control', 'rows': 2}),
            # 'high_temp_simul_test': forms. Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        
        # Set 'form-control' class for all fields by default
        for field_name, field in self.fields.items():
            if hasattr(field, 'widget'):
                field.widget.attrs['class'] = 'form-control'
 
        # Dynamically set widgets for fields with specific choices
        self.fields['first_article_type'].widget = forms. Select(choices=FAI_SITUATION_CHOICES, attrs={'class': 'form-control'})
        self.fields['qe_confirm_status'].widget = forms. Select(choices=FORM_APPROVAL, attrs={'class': 'form-control'})
 
        # Set widgets for standard check and result fields
        for field_name, field in self.fields.items():
            if field_name.endswith('_check') and not field_name.endswith('_evidence'):
                field.widget = forms. Select(choices=FORM_CHOICES, attrs={'class': 'form-control status-select'})
                if field_name.endswith('_result'):
                    field.widget = forms. Select(choices=FORM_RESULT_CHOICES, attrs={'class': 'form-control status-select'})
 
        # Set specific fields as required
        required_fields = [
            'date', 'shift', 'emp_id', 'name', 'section', 'line', 'group', 'model', 'color',
            'production_work_order_no', 'first_article_type', 'sample_serial_number', 
            'imei_number', 'visual_functional_result', 'reliability_result'
        ]
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True
 
    def clean_date(self):
        """Ensure the inspection date is not in the future."""
        date = self.cleaned_data.get('date')
        if date and date > timezone.now().date():
            raise forms. ValidationError("Inspection date cannot be in the future.")
        return date
 
    def clean_imei_number(self):
        """Validate IMEI format."""
        imei = self.cleaned_data.get('imei_number')
        if imei:
            imei_stripped = imei.replace(' ', '')
            if len(imei_stripped) != 15 or not imei_stripped.isdigit():
                raise forms. ValidationError("IMEI must be exactly 15 digits.")
            return imei_stripped
        return imei
 
    def validate_image_file(self, image_file, max_size=5*1024*1024):
        """Validate an uploaded image file for size, type, and dimensions."""
        if not image_file:
            return None
        if image_file.size > max_size:
            raise forms. ValidationError(f"Image file size cannot exceed {max_size//(1024*1024)}MB.")
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'image/bmp']
        file_type = mimetypes.guess_type(image_file.name)[0]
        if file_type not in allowed_types:
            raise forms. ValidationError("Only JPEG, PNG, and BMP image formats are allowed.")
        try:
            from PIL import Image
            img = Image. open(image_file)
            img.verify()
        except Exception:
            raise forms. ValidationError("Invalid or corrupted image file.")
        return image_file
 
    
 
    # --- Individual Field Validation for Evidence Files ---
    def clean_label_check_evidence(self): return self.validate_image_file(self.cleaned_data.get('label_check_evidence'))
    def clean_label_position_check_evidence(self): return self.validate_image_file(self.cleaned_data.get('label_position_check_evidence'))
    def clean_logo_check_evidence(self): return self.validate_image_file(self.cleaned_data.get('logo_check_evidence'))
    def clean_assembly_battery_check_evidence(self): return self.validate_image_file(self.cleaned_data.get('assembly_battery_check_evidence'))
    def clean_boot_time_test_evidence(self): return self.validate_image_file(self.cleaned_data.get('boot_time_test_evidence'))
    def clean_camera_front_test_evidence(self): return self.validate_image_file(self.cleaned_data.get('camera_front_test_evidence'))
    def clean_camera_back_test_evidence(self): return self.validate_image_file(self.cleaned_data.get('camera_back_test_evidence'))
    def clean_camera_dark_test_evidence(self): return self.validate_image_file(self.cleaned_data.get('camera_dark_test_evidence'))
    def clean_high_temp_camera_test_evidence(self): return self.validate_image_file(self.cleaned_data.get('high_temp_camera_test_evidence'))
    def clean_imei_photo(self): return self.validate_image_file(self.cleaned_data.get('imei_photo'))
 
    def clean(self):
        """Custom cross-field validation."""
        cleaned_data = super().clean()
        visual_result = cleaned_data.get('visual_functional_result')
        reliability_result = cleaned_data.get('reliability_result')
        if (visual_result == 'UNQUALIFIED' or reliability_result == 'UNQUALIFIED') and not cleaned_data.get('inspector_name'):
            self.add_error('inspector_name', "Inspector name is required when a result is 'Unqualified'.")
        return cleaned_data
 
    def save(self, commit=True):
        """Override save to auto-populate inspector name."""
        instance = super().save(commit=False)

        user = self.user  # ✅ use self.user, not self.request.user
        if user and not instance.inspector_name:
            inspector_name = (
                getattr(user, 'full_name', None)
                or getattr(user, 'name', None)
                or getattr(user, 'username', None)
                or str(user)
            )
            instance.inspector_name = inspector_name  # ✅ actually assign it

        if commit:
            instance.save()
        return instance
    
class OperatorQualificationCheckForm(forms.ModelForm):
    class Meta:
        model = OperatorQualificationCheck
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'job_card_verification_summary': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'scanned_barcode_text': forms.URLInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'scanned_barcode_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'key_station_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        for field in self.fields.values():
            if field.widget.__class__.__name__ not in ['CheckboxInput', 'RadioSelect']:
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'

        # Read-only fields
        readonly_fields = ['emp_id','name','date','shift','section','line','group','model','color']
        for field in readonly_fields:
            if field in self.fields:
                self.fields[field].widget.attrs['readonly'] = True