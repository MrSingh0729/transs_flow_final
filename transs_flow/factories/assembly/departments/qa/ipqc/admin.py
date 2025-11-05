from django.contrib import admin
from .models import (
    IPQCWorkInfo,
    DynamicForm,
    DynamicFormField,
    DynamicFormSubmission,
    IPQCAssemblyAudit,
    BTBFitmentChecksheet,
    AssDummyTest,
    IPQCDisassembleCheckList,
)

# --- IPQC Work Info ---
@admin.register(IPQCWorkInfo)
class IPQCWorkInfoAdmin(admin.ModelAdmin):
    list_display = ('date', 'shift', 'emp_id', 'name', 'section', 'line', 'model')
    list_filter = ('shift', 'section', 'line', 'model')
    search_fields = ('emp_id', 'name', 'model')

# --- Dynamic Form & Fields ---
class DynamicFormFieldInline(admin.TabularInline):
    model = DynamicFormField
    extra = 1

@admin.register(DynamicForm)
class DynamicFormAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'lark_bitable_table_id', 'created_at')
    inlines = [DynamicFormFieldInline]
    search_fields = ('title', 'description', 'lark_bitable_table_id')

@admin.register(DynamicFormSubmission)
class DynamicFormSubmissionAdmin(admin.ModelAdmin):
    list_display = ('form', 'submitted_by', 'created_at')
    list_filter = ('form', 'submitted_by')
    search_fields = ('form__title', 'submitted_by__username')

# --- IPQC Assembly Audit ---
@admin.register(IPQCAssemblyAudit)
class IPQCAssemblyAuditAdmin(admin.ModelAdmin):
    list_display = ('date', 'shift', 'emp_id', 'name', 'section', 'line', 'model', 'color')
    list_filter = ('shift', 'section', 'line', 'model')
    search_fields = ('emp_id', 'name', 'model')

# --- BTB Fitment Checksheet ---
@admin.register(BTBFitmentChecksheet)
class BTBFitmentChecksheetAdmin(admin.ModelAdmin):
    list_display = ('date', 'shift', 'emp_id', 'name', 'line', 'model', 'grand_total')
    list_filter = ('shift', 'line', 'model')
    search_fields = ('emp_id', 'name', 'model')

# --- Ass Dummy Test ---
@admin.register(AssDummyTest)
class AssDummyTestAdmin(admin.ModelAdmin):
    list_display = ('date', 'shift', 'emp_id', 'name', 'line', 'group', 'test_item', 'result')
    list_filter = ('shift', 'line', 'group', 'result')
    search_fields = ('emp_id', 'name', 'model', 'test_item')

# --- IPQC Disassemble Checklist ---
@admin.register(IPQCDisassembleCheckList)
class IPQCDisassembleCheckListAdmin(admin.ModelAdmin):
    list_display = ('date', 'shift', 'emp_id', 'name', 'line', 'model', 'color')
    list_filter = ('shift', 'line', 'model')
    search_fields = ('emp_id', 'name', 'model')
