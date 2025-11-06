import requests
from datetime import datetime
import pytz
from django.conf import settings
from .models import BTBFitmentChecksheet


def get_feishu_access_token():
    """Get Feishu access token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
    headers = {"Content-Type": "application/json"}
    data = {
        "app_id": getattr(settings, "FEISHU_APP_ID", None),
        "app_secret": getattr(settings, "FEISHU_APP_SECRET", None)
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        json_data = response.json()
        return json_data.get("tenant_access_token")
    except Exception as e:
        print("❌ Feishu token error:", e)
        return None


def fetch_feishu_bitable_record(record_id, app_id, table_id):
    """Fetch a single record from Feishu Bitable"""
    token = get_feishu_access_token()
    if not token:
        return None

    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_id}/tables/{table_id}/records/{record_id}"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("❌ Feishu fetch record error:", e)
        return None


def extract_required_fields_feishu(record_data):
    """Extract only the required fields from Feishu record payload"""
    try:
        docs_pc = record_data.get('data', {}).get('docs_pc', {})
        if not docs_pc:
            return None
        
        # Assuming we want the first item in the list
        first_item = docs_pc.get('list', [{}])[0]

        required = {
            "emp_id": first_item.get("emp_id"),
            "name": first_item.get("name"),
            "group": first_item.get("group"),
            "department": first_item.get("department"),
            "ctq_stage": first_item.get("ctq_stage"),
            "total_marks": first_item.get("total_marks")
        }
        return required
    except Exception as e:
        print("Field extraction error:", e)
        return None

def get_lark_access_token():
    """Get Lark access token"""
    url = "https://open.larkoffice.com/open-apis/auth/v3/tenant_access_token/internal/"
    headers = {"Content-Type": "application/json"}
    data = {
        "app_id": getattr(settings, "LARK_APP_ID", None),
        "app_secret": getattr(settings, "LARK_APP_SECRET", None)
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        json_data = response.json()
        # print("🪶 Access token response:", json_data)
        return json_data.get("tenant_access_token")
    except Exception as e:
        print("❌ Token error:", e)
        return None


def date_to_ms(date_obj):
    """Convert datetime.date or ISO date string to milliseconds since epoch (IST)"""
    ist = pytz.timezone('Asia/Kolkata')

    if isinstance(date_obj, str):
        # Convert ISO string to date object
        date_obj = datetime.strptime(date_obj, "%Y-%m-%d").date()

    ist_datetime = ist.localize(datetime.combine(date_obj, datetime.min.time()))
    return int(ist_datetime.timestamp() * 1000)


# def write_to_bitable(work_info):
#     """Write work info to Lark Bitable"""
#     token = get_lark_access_token()
#     if not token:
#         print("❌ No token received")
#         return False, "Failed to get Lark access token"

#     url = (
#         f"https://open.larkoffice.com/open-apis/bitable/v1/apps/"
#         f"{getattr(settings, 'LARK_BITABLE_APP_TOKEN_QA')}/tables/"
#         f"{getattr(settings, 'LARK_TABLE_IPQC_WORK_INFO')}/records"
#     )

#     headers = {
#         "Authorization": f"Bearer {token}",
#         "Content-Type": "application/json"
#     }

#     data = {
#         "fields": {
#             "Date": date_to_ms(work_info.date),
#             "Shift": work_info.shift,
#             "Emp_ID": work_info.emp_id,
#             "Name": work_info.name,
#             "Section": work_info.section,
#             "Line": work_info.line,
#             "Group": work_info.group,
#             "Model": work_info.model,
#             "Color": work_info.color,
#         }
#     }

#     # print("📤 Sending to Lark Bitable:", data)

#     try:
#         response = requests.post(url, headers=headers, json=data)
#         resp_json = response.json()
#         # print("📥 Response from Lark:", resp_json)

#         if response.status_code == 200 and resp_json.get("code") == 0:
#             return True, "Successfully synced to Lark Bitable"

#         return False, resp_json.get("msg", response.text)
#     except Exception as e:
#         # print("❌ Exception:", e)
#         return False, f"Error syncing to Lark Bitable: {str(e)}"


def write_to_bitable(work_info):
    """Write work info to Lark Bitable"""
    token = get_lark_access_token()
    if not token:
        return False, "Failed to get Lark access token"

    url = (
        f"https://open.larkoffice.com/open-apis/bitable/v1/apps/"
        f"{getattr(settings, 'LARK_BITABLE_APP_TOKEN_QA')}/tables/"
        f"{getattr(settings, 'LARK_TABLE_IPQC_WORK_INFO')}/records"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = {
        "fields": {
            "Date": date_to_ms(work_info.date),
            "Shift": work_info.shift,
            "Emp_ID": work_info.emp_id,
            "Name": work_info.name,
            "Section": work_info.section,
            "Line": work_info.line,
            "Group": work_info.group,
            "Model": work_info.model,
            "Color": work_info.color,
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        resp_json = response.json()

        if response.status_code == 200 and resp_json.get("code") == 0:
            return True, "Successfully synced to Lark Bitable"
        return False, resp_json.get("msg", response.text)
    except Exception as e:
        return False, f"Error syncing to Lark Bitable: {str(e)}"



def write_to_bitable_dynamic(table_id, data):
    """Write any model data to Lark Bitable table"""
    token = get_lark_access_token()
    if not token:
        return False, "Failed to get Lark access token"

    url = (
        f"https://open.larkoffice.com/open-apis/bitable/v1/apps/"
        f"{getattr(settings, 'LARK_BITABLE_APP_TOKEN_QA')}/tables/{table_id}/records"
    )

    # Convert datetime fields to ms
    for key, value in data.items():
        if isinstance(value, datetime):
            ist = pytz.timezone('Asia/Kolkata')
            # Only localize naive datetimes
            if value.tzinfo is None:
                value = ist.localize(value)
            data[key] = int(value.timestamp() * 1000)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {"fields": data}

    try:
        response = requests.post(url, headers=headers, json=payload)
        resp_json = response.json()
        if response.status_code == 200 and resp_json.get("code") == 0:
            return True, "Successfully synced to Lark Bitable"
        return False, resp_json.get("msg", response.text)
    except Exception as e:
        return False, f"Error syncing to Lark Bitable: {str(e)}"
    
    
    

def safe_int(val):
    """Convert value to integer safely."""
    try:
        return int(val or 0)
    except (TypeError, ValueError):
        return 0

def sync_btb_fitment_to_bitable(instance):
    """
    Sync a single BTB Fitment Checksheet record to Lark Bitable.
    """
    token = get_lark_access_token()
    if not token:
        print("❌ No access token, skipping Bitable sync.")
        return False, "No access token"

    table_id = getattr(settings, "LARK_TABLE_BTB_FITMENT_CHECKSHEET", None)
    if not table_id:
        print("❌ Table ID missing in settings.")
        return False, "Table ID missing"

    url = f"https://open.larkoffice.com/open-apis/bitable/v1/apps/{settings.LARK_BITABLE_APP_TOKEN_QA}/tables/{table_id}/records"

    # Build fields dict
    fields = {
        # Text fields
        "Date": date_to_ms(instance.date),
        "Shift": instance.shift or "",
        "Employee ID": instance.emp_id or "",
        "Employee Name": instance.name or "",
        "Line": instance.line or "",
        "Group": instance.group or "",
        "Model": instance.model or "",
        "Colour": instance.color or "",
        "Frequency": instance.frequency or "",
        "Submitted By": instance.name or "",
        "Created At": date_to_ms(instance.created_at),

        # Numeric fields
        "Input - 9:00": safe_int(instance.input_9),
        "Input - 10:00": safe_int(instance.input_10),
        "Input - 11:00": safe_int(instance.input_11),
        "Input - 12:00": safe_int(instance.input_12),
        "Input - 1:00": safe_int(instance.input_1),
        "Input - 2:00": safe_int(instance.input_2),
        "Input - 3:00": safe_int(instance.input_3),
        "Input - 4:00": safe_int(instance.input_4),
        "Input - 5:00": safe_int(instance.input_5),
        "Input - 6:00": safe_int(instance.input_6),
        "Input - Total": safe_int(instance.input_total),

        "CAM BTB - 9:00": safe_int(instance.cam_btb_9),
        "CAM BTB - 10:00": safe_int(instance.cam_btb_10),
        "CAM BTB - 11:00": safe_int(instance.cam_btb_11),
        "CAM BTB - 12:00": safe_int(instance.cam_btb_12),
        "CAM BTB - 1:00": safe_int(instance.cam_btb_1),
        "CAM BTB - 2:00": safe_int(instance.cam_btb_2),
        "CAM BTB - 3:00": safe_int(instance.cam_btb_3),
        "CAM BTB - 4:00": safe_int(instance.cam_btb_4),
        "CAM BTB - 5:00": safe_int(instance.cam_btb_5),
        "CAM BTB - 6:00": safe_int(instance.cam_btb_6),
        "CAM BTB - Total": safe_int(instance.cam_btb_total),

        "LCD Fitment - 9:00": safe_int(instance.lcd_fitment_9),
        "LCD Fitment - 10:00": safe_int(instance.lcd_fitment_10),
        "LCD Fitment - 11:00": safe_int(instance.lcd_fitment_11),
        "LCD Fitment - 12:00": safe_int(instance.lcd_fitment_12),
        "LCD Fitment - 1:00": safe_int(instance.lcd_fitment_1),
        "LCD Fitment - 2:00": safe_int(instance.lcd_fitment_2),
        "LCD Fitment - 3:00": safe_int(instance.lcd_fitment_3),
        "LCD Fitment - 4:00": safe_int(instance.lcd_fitment_4),
        "LCD Fitment - 5:00": safe_int(instance.lcd_fitment_5),
        "LCD Fitment - 6:00": safe_int(instance.lcd_fitment_6),
        "LCD Fitment - Total": safe_int(instance.lcd_fitment_total),

        "MAIN FPC - 9:00": safe_int(instance.main_fpc_9),
        "MAIN FPC - 10:00": safe_int(instance.main_fpc_10),
        "MAIN FPC - 11:00": safe_int(instance.main_fpc_11),
        "MAIN FPC - 12:00": safe_int(instance.main_fpc_12),
        "MAIN FPC - 1:00": safe_int(instance.main_fpc_1),
        "MAIN FPC - 2:00": safe_int(instance.main_fpc_2),
        "MAIN FPC - 3:00": safe_int(instance.main_fpc_3),
        "MAIN FPC - 4:00": safe_int(instance.main_fpc_4),
        "MAIN FPC - 5:00": safe_int(instance.main_fpc_5),
        "MAIN FPC - 6:00": safe_int(instance.main_fpc_6),
        "MAIN FPC - Total": safe_int(instance.main_fpc_total),

        "Battery - 9:00": safe_int(instance.battery_9),
        "Battery - 10:00": safe_int(instance.battery_10),
        "Battery - 11:00": safe_int(instance.battery_11),
        "Battery - 12:00": safe_int(instance.battery_12),
        "Battery - 1:00": safe_int(instance.battery_1),
        "Battery - 2:00": safe_int(instance.battery_2),
        "Battery - 3:00": safe_int(instance.battery_3),
        "Battery - 4:00": safe_int(instance.battery_4),
        "Battery - 5:00": safe_int(instance.battery_5),
        "Battery - 6:00": safe_int(instance.battery_6),
        "Battery - Total": safe_int(instance.battery_total),

        "Finger Printer - 9:00": safe_int(instance.finger_printer_9),
        "Finger Printer - 10:00": safe_int(instance.finger_printer_10),
        "Finger Printer - 11:00": safe_int(instance.finger_printer_11),
        "Finger Printer - 12:00": safe_int(instance.finger_printer_12),
        "Finger Printer - 1:00": safe_int(instance.finger_printer_1),
        "Finger Printer - 2:00": safe_int(instance.finger_printer_2),
        "Finger Printer - 3:00": safe_int(instance.finger_printer_3),
        "Finger Printer - 4:00": safe_int(instance.finger_printer_4),
        "Finger Printer - 5:00": safe_int(instance.finger_printer_5),
        "Finger Printer - 6:00": safe_int(instance.finger_printer_6),
        "Finger Printer - Total": safe_int(instance.finger_printer_total),

        "Total - 9:00": safe_int(instance.total_9),
        "Total - 10:00": safe_int(instance.total_10),
        "Total - 11:00": safe_int(instance.total_11),
        "Total - 12:00": safe_int(instance.total_12),
        "Total - 1:00": safe_int(instance.total_1),
        "Total - 2:00": safe_int(instance.total_2),
        "Total - 3:00": safe_int(instance.total_3),
        "Total - 4:00": safe_int(instance.total_4),
        "Total - 5:00": safe_int(instance.total_5),
        "Total - 6:00": safe_int(instance.total_6),

        # Remarks (Text)
        "Remark - Input": instance.remark_input or "",
        "Remark - CAM BTB": instance.remark_cam_btb or "",
        "Remark - LCD Fitment": instance.remark_lcd_fitment or "",
        "Remark - MAIN FPC": instance.remark_main_fpc or "",
        "Remark - Battery": instance.remark_battery or "",
        "Remark - Finger Printer": instance.remark_finger_printer or "",

        # Grand Total (Text)
        "Grand Total": instance.grand_total,
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json={"fields": fields})
        resp_json = response.json()
        if response.status_code == 200 and resp_json.get("code") == 0:
            print(f"✅ Record synced successfully: {resp_json.get('data', {}).get('record_id')}")
            return True, "Synced successfully"
        else:
            print("❌ Bitable sync failed:", resp_json)
            return False, resp_json
    except Exception as e:
        print("❌ Exception syncing to Bitable:", str(e))
        return False, str(e)
    
    
def sync_dummy_test_to_bitable(instance):
    """
    Sync a single BTB Fitment Checksheet record to Lark Bitable.
    """
    token = get_lark_access_token()
    if not token:
        print("❌ No access token, skipping Bitable sync.")
        return False, "No access token"

    table_id = getattr(settings, "LARK_TABLE_BUMMY_CHECKSHEET", None)
    if not table_id:
        print("❌ Table ID missing in settings.")
        return False, "Table ID missing"

    url = f"https://open.larkoffice.com/open-apis/bitable/v1/apps/{settings.LARK_BITABLE_APP_TOKEN_QA}/tables/{table_id}/records"

    # Build fields dict
    fields = {
        # Text / Boolean fields
        "Date": date_to_ms(instance.date),
        "Shift": instance.shift or "",
        "Emp ID": instance.emp_id or "",
        "Name": instance.name or "",
        "Area": instance.area or "",
        "Section": instance.section or "",
        "Line": instance.line or "",
        "Group": instance.group or "",
        "Model": instance.model or "",
        "Color": instance.color or "",
        "Test Stage": instance.test_stage or "",
        "Test Item": instance.test_item or "",
        "Operator Name": instance.operator_name or "",
        "Operator ID": instance.operator_id or "",
        "Result": instance.result or "",
        "Cause": instance.cause or "",
        "Measure": instance.measure or "",
        "LL Confirm": "Yes" if instance.ll_confirm else "No",  # ✅ Convert boolean to string
        "Remark": instance.remark or "",
        "Created At": date_to_ms(instance.created_at),
        "Updated At": date_to_ms(instance.updated_at),
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json={"fields": fields})
        resp_json = response.json()
        if response.status_code == 200 and resp_json.get("code") == 0:
            print(f"✅ Record synced successfully: {resp_json.get('data', {}).get('record_id')}")
            return True, "Synced successfully"
        else:
            print("❌ Bitable sync failed:", resp_json)
            return False, resp_json
    except Exception as e:
        print("❌ Exception syncing to Bitable:", str(e))
        return False, str(e)
    
    
def sync_dessembly_checklist_to_bitable(instance):
    """
    Sync a single BTB Fitment Checksheet record to Lark Bitable.
    """
    token = get_lark_access_token()
    if not token:
        print("❌ No access token, skipping Bitable sync.")
        return False, "No access token"

    table_id = getattr(settings, "LARK_TABLE_DESSEMBLE_CHECKLIST", None)
    if not table_id:
        print("❌ Table ID missing in settings.")
        return False, "Table ID missing"

    url = f"https://open.larkoffice.com/open-apis/bitable/v1/apps/{settings.LARK_BITABLE_APP_TOKEN_QA}/tables/{table_id}/records"

    # Build fields dict
    fields = {
        # Work Info
        "Date": date_to_ms(instance.date),
        "Shift": instance.shift or "",
        "Employee ID": instance.emp_id or "",
        "Employee Name": instance.name or "",
        "Section": instance.section or "",
        "Line": instance.line or "",
        "Group": instance.group or "",
        "Model": instance.model or "",
        "Color": instance.color or "",

        # Test Fields (OK / Not OK / NA)
        "Colour Match": instance.color_match or "",
        "TP SOP": instance.tp_sop or "",
        "Camera Lens": instance.cam_lens or "",
        "Key Feel": instance.key_feel or "",
        "Screw Check": instance.screw_check or "",
        "Front Housing": instance.front_housing or "",
        "Back Housing": instance.back_housing or "",
        "Proof Label": instance.proof_label or "",
        "Mic SOP": instance.mic_sop or "",
        "LED SOP": instance.led_sop or "",
        "Coaxial Line": instance.coaxial or "",
        "LCD SOP": instance.lcd_sop or "",
        "Speaker SOP": instance.speaker_sop or "",
        "Motor SOP": instance.motor_sop or "",
        "Key SOP": instance.key_sop or "",
        "SIM Subboard": instance.sim_subboard or "",
        "Subboard SOP": instance.subboard_sop or "",
        "Antenna Shrapnel": instance.antenna_shrapnel or "",
        "Conductive Fabric": instance.conductive_fabric or "",
        "Insulation Paste": instance.insulation_paste or "",
        "Camera SOP": instance.camera_sop or "",
        "Mainboard OK": instance.mainboard_ok or "",
        "Antenna FPC": instance.antenna_fpc or "",
        "Front Accessory": instance.front_acc or "",
        "LCD Fabric": instance.lcd_fabric or "",
        "Receiver SOP": instance.receiver_sop or "",
        "LCD FPC Defect": instance.lcd_fpc_defect or "",
        "TP FPC Defect": instance.tp_fpc_defect or "",
        "Key FPC Solder": instance.key_fpc_solder or "",
        "Keypad Defect": instance.keypad_defect or "",
        "Solder Splash": instance.solder_splash or "",
        "Foam Stick": instance.foam_stick or "",
        "Camera Glue": instance.cam_glue or "",
        "Paste Cover": instance.ins_paste_cover or "",
        "LED Position": instance.led_position or "",
        "Jig/Fixture Test": instance.jig_fixture_test or "",
        "Glue Location": instance.glue_location or "",

        # IMEI & Remarks
        "IMEI 1": instance.imei1 or "",
        "IMEI 2": instance.imei2 or "",
        "Defect cause analysis": instance.defect_cause or "",
        "PQE": instance.pqe or "",
        "PE": instance.pe or "",
        "APD LL": instance.apd_ll or "",

        # System Fields
        "Created At": date_to_ms(instance.created_at),
        "Updated At": date_to_ms(instance.updated_at),
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json={"fields": fields})
        resp_json = response.json()
        if response.status_code == 200 and resp_json.get("code") == 0:
            print(f"✅ Record synced successfully: {resp_json.get('data', {}).get('record_id')}")
            return True, "Synced successfully"
        else:
            print("❌ Bitable sync failed:", resp_json)
            return False, resp_json
    except Exception as e:
        print("❌ Exception syncing to Bitable:", str(e))
        return False, str(e)
    
    
    
def sync_ipqc_assembly_audit_to_bitable(instance):
    token = get_lark_access_token()
    if not token:
        print("❌ No access token, skipping sync.")
        return False, "No access token"

    table_id = getattr(settings, "LARK_TABLE_ASSEMBLY_AUDIT", None)
    if not table_id:
        print("❌ Table ID missing in settings.")
        return False, "Table ID missing"

    url = f"https://open.larkoffice.com/open-apis/bitable/v1/apps/{settings.LARK_BITABLE_APP_TOKEN_QA}/tables/{table_id}/records"

    fields = {
        # --- BASIC INFO ---
        "Date": date_to_ms(instance.date),
        "Shift": instance.shift or "",
        "IPQC Name": instance.name or "",
        "Employee ID": instance.emp_id or "",
        "Section": instance.section or "",
        "Group": instance.group or "",
        "Line": instance.line or "",
        "Model": instance.model or "",
        "Colour": instance.color or "",
        "Created At": date_to_ms(instance.created_at),

        # --- MAN ---
        "Job Card Availability": instance.man_job_card or "",
        "BTB Monitoring Guideline": instance.man_btb_mon or "",

        # --- MACHINE ---
        "EPA Check": instance.mach_epa_check or "",
        "Screw Torque": instance.mach_screw_torque or "",
        "Light Illuminance": instance.mach_light or "",
        "Fixture Cleanliness": instance.mach_fixture_clean or "",
        "Jig Label Validity": instance.mach_jig_label or "",
        "Teflon Condition": instance.mach_teflon or "",
        "Press Parameters": instance.mach_press_params or "",
        "Glue Parameters": instance.mach_glue_params or "",
        "Equipment Move Notification": instance.mach_eq_move_notify or "",
        "Feeler Gauge Check": instance.mach_feeler_gauge or "",
        "Hot/Cold Press Parameters": instance.mach_hot_cold_press or "",
        "Ion Fan Position": instance.mach_ion_fan or "",
        "Clean Room Equipment": instance.mach_cleanroom_eq or "",
        "RTI Check": instance.mach_rti_check or "",
        "Current Test Parameters": instance.mach_current_test or "",
        "PAL QR Check": instance.mach_pal_qr or "",
        "Automatic Screwing": instance.mach_auto_screw or "",

        # --- MATERIAL ---
        "Key Material Check": instance.mat_key_check or "",
        "Special Stop Material": instance.mat_special_stop or "",
        "Improved Material Monitor": instance.mat_improved_monitor or "",
        "Material Result Check": instance.mat_result_check or "",
        "Battery Issue Handling": instance.mat_battery_issue or "",
        "IPA Usage Check": instance.mat_ipa_check or "",
        "Thermal Gel Check": instance.mat_thermal_gel or "",
        "Material Verification": instance.mat_verification or "",

        # --- METHOD ---
        "SOP Sequence Verification": instance.meth_sop_seq or "",
        "Distance Sensor Height": instance.meth_distance_sensor or "",
        "Rear Camera Seal Check": instance.meth_rear_camera or "",
        "Material Handling": instance.meth_material_handling or "",
        "Guideline Document": instance.meth_guideline_doc or "",
        "Operation Document": instance.meth_operation_doc or "",
        "Defective Feedback Process": instance.meth_defective_feedback or "",
        "Line Record Verification": instance.meth_line_record or "",
        "No Self Repair": instance.meth_no_self_repair or "",
        "Battery Fix Check": instance.meth_battery_fix or "",
        "Line Change Verification": instance.meth_line_change or "",
        "Trial Run Monitoring": instance.meth_trail_run or "",
        "Dummy Conduct Check": instance.meth_dummy_conduct or "",

        # --- ENVIRONMENT ---
        "Production Environment Monitoring": instance.env_prod_monitor or "",
        "5S Check": instance.env_5s or "",

        # --- TRC / FAI / DEFECT / SPOT CHECK ---
        "TRC Flow Chart": instance.trc_flow_chart or "",
        "FAI Check": instance.fai_check or "",
        "Defect Monitoring": instance.defect_monitor or "",
        "Spot Check": instance.spot_check or "",
        "Auto Screw Sampling": instance.auto_screw_sample or "",

        # --- MANUAL INPUT ---
        "Manufacture": instance.manufacture or "",
        "Work Order": instance.work_order or "",
        "Brand": instance.brand or "",
        "Material Code": instance.material_code or "",
        "WO / Input Qty": instance.wo_input_qty or "",

        # --- TOP 3 DEFECTS & REMARKS ---
        "Top 3 Defects": instance.top3_defects or "",
        "Remarks": instance.remarks or "",

        # --- SIGNATURES ---
        "IPQC Sign": instance.ipqc_sign or "",
        "PQE/TL Sign": instance.pqe_tl_sign or "",
    }

    payload = {"fields": fields}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json={"fields": fields})
    res_json = response.json()
    if response.status_code == 200 and res_json.get("code") == 0:
        print("✅ Synced successfully to Bitable.")
    else:
        print(f"⚠️ Sync failed: {res_json}")
        
        
        
def sync_nc_issue_tracking_to_bitable(instance):
    token = get_lark_access_token()
    if not token:
        print("❌ No access token, skipping sync.")
        return False, "No access token"

    table_id = getattr(settings, "LARK_TABLE_NC_ISSUE_TRACKING", None)
    if not table_id:
        print("❌ Table ID missing in settings.")
        return False, "Table ID missing"

    url = f"https://open.larkoffice.com/open-apis/bitable/v1/apps/{settings.LARK_BITABLE_APP_TOKEN_QA}/tables/{table_id}/records"

    fields = {
        # Work Info
        "Date": date_to_ms(instance.date),
        "Shift": instance.shift or "",
        "Employee ID": instance.emp_id or "",
        "Employee Name": instance.name or "",
        "Section": instance.section or "",
        "Line": instance.line or "",
        "Group": instance.group or "",
        "Model": instance.model or "",
        "Color": instance.color or "",

        # Issue Tracking
        "Stage": instance.stage or "",
        "Time": date_to_ms(instance.date),  # timestamp from TimeField
        "Issue": instance.issue or "",
        "3 Why": instance.three_why or "",
        "Solution": instance.solution or "",
        "Operator Name": instance.operator_name or "",
        "Operator ID": instance.operator_id or "",
        "Responsible Dept.": instance.responsible_dept or "",
        "Responsible Person": instance.responsible_person or "",
        "Close Time": date_to_ms(instance.close_time) if instance.close_time else "",
        "Status": instance.status or "",
        "Remark": instance.remark or "",

        # System Fields
        "Created At": date_to_ms(instance.created_at),
        "Updated At": date_to_ms(instance.updated_at),
    }

    payload = {"fields": fields}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json={"fields": fields})
    res_json = response.json()
    if response.status_code == 200 and res_json.get("code") == 0:
        print("✅ Synced successfully to Bitable.")
    else:
        print(f"⚠️ Sync failed: {res_json}")
        
def sync_esd_compliance_to_bitable(instance):
    token = get_lark_access_token()
    if not token:
        print("❌ No access token, skipping sync.")
        return False, "No access token"

    table_id = getattr(settings, "LARK_TABLE_ESD_COMPLIANCE", None)
    if not table_id:
        print("❌ Table ID missing in settings.")
        return False, "Table ID missing"

    url = f"https://open.larkoffice.com/open-apis/bitable/v1/apps/{settings.LARK_BITABLE_APP_TOKEN_QA}/tables/{table_id}/records"

    fields = {
        "Date": date_to_ms(instance.date),
        "Shift": instance.shift,
        "Employee ID": instance.emp_id,
        "Name": instance.name,
        "Line": instance.line,
        "Group": instance.group,
        "Model": instance.model,
        "Color": instance.color,
        "EPA Wear ESD Clothes": str(instance.epa_clothes),
        "No ESD Clothes Outside": str(instance.forbid_wear_out),
        "No Accessories on Clothes": str(instance.no_accessories),
        "Clothes Clean & Tidy": str(instance.clothes_clean),
        "Collar & Button Rules": str(instance.collar_rules),
        "Hair Inside Cap": str(instance.hair_cap),
        "Check Slipper & Band": str(instance.slipper_band),
        "Wrist Band Precheck": str(instance.pre_line_check),
        "Wrist Band Touch Skin": str(instance.wrist_touch_skin),
        "No Touch PCBA/ESDS": str(instance.no_touch_pcba),
        "Alert When Plug Out": str(instance.alert_plug_out),
        "Trolley Grounded": str(instance.trolley_grounding),
        "Ion Fan Distance OK": str(instance.ion_fan_distance),
        "Ion Fan Direction OK": str(instance.ion_fan_direction),
        "Audit Label Valid": str(instance.audit_label_valid),
        "Devices Grounded": str(instance.device_grounded),
        "Gloves/Fingers OK": str(instance.gloves_condition),
        "Mat Grounded": str(instance.mat_grounded),
        "ESDS in ESD Box": str(instance.esds_box),
        "Table No ESD Source": str(instance.table_no_source),
        "Tools Daily Audit": str(instance.tools_audit),
        "Temp & Humidity SPEC": str(instance.temp_humidity),
        "Tray Voltage < ±100V": str(instance.tray_voltage),
        "Remark": instance.remark or "",
        "Created At": date_to_ms(instance.created_at),
        "Updated At": date_to_ms(instance.updated_at),
    }

    payload = {"fields": fields}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json={"fields": fields})
    res_json = response.json()
    if response.status_code == 200 and res_json.get("code") == 0:
        print("✅ Synced successfully to Bitable.")
    else:
        print(f"⚠️ Sync failed: {res_json}")
        
def sync_dust_measurement_to_bitable(instance):
    token = get_lark_access_token()
    if not token:
        print("❌ No access token, skipping sync.")
        return False, "No access token"

    table_id = getattr(settings, "LARK_TABLE_DUST_MEASUREMENT", None)
    if not table_id:
        print("❌ Table ID missing in settings.")
        return False, "Table ID missing"

    url = f"https://open.larkoffice.com/open-apis/bitable/v1/apps/{settings.LARK_BITABLE_APP_TOKEN_QA}/tables/{table_id}/records"

    fields = {
        "Date": date_to_ms(instance.date),
        "Shift": instance.shift,
        "Employee ID": instance.emp_id,
        "Name": instance.name,
        "Line": instance.line,
        "Group": instance.group,
        "Model": instance.model,
        "Color": instance.color,
        "≥0.3 micrometer": instance.micrometer_0_3,
        "≥0.5 micrometer": instance.micrometer_0_5,
        "≥1.0 micrometer": instance.micrometer_1_0,
        "Checked By": instance.checked_by,
        "Verified By": instance.verified_by,
        "Remark": instance.remark or "",
        "Created At": date_to_ms(instance.created_at),
        "Updated At": date_to_ms(instance.updated_at),
    }

    payload = {"fields": fields}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json={"fields": fields})
    res_json = response.json()
    if response.status_code == 200 and res_json.get("code") == 0:
        print("✅ Synced successfully to Bitable.")
    else:
        print(f"⚠️ Sync failed: {res_json}")
        
 
       
def sync_testing_fai_to_bitable(instance):
    token = get_lark_access_token()
    if not token:
        print("❌ No access token, skipping sync.")
        return False, "No access token"

    table_id = getattr(settings, "LARK_TABLE_TESTING_FAI", None)
    if not table_id:
        print("❌ Table ID missing in settings.")
        return False, "Table ID missing"

    url = f"https://open.larkoffice.com/open-apis/bitable/v1/apps/{settings.LARK_BITABLE_APP_TOKEN_QA}/tables/{table_id}/records"

    fields = {
        "Date": date_to_ms(instance.date),
        "Shift": instance.shift,
        "Employee ID": instance.emp_id,
        "Employee Name": instance.name,
        "Section": instance.section,
        "Line": instance.line,
        "Group": instance.group,
        "Model": instance.model,
        "Color": instance.color,
        "Production Work Order No": instance.production_work_order_no,
        "First Article Type": instance.first_article_type,
        "Software Version Check": instance.software_ver_check,
        "Android Version Check": instance.android_ver_check,
        "Memory Inbuilt Check Result": instance.memory_inbuilt_check,
        "Order Confirmation Check": instance.order_confirm_check,
        "Label Check": instance.label_check,
        # "Label Photo": instance.label_check_evidence.url if instance.label_check_evidence else "",
        "Label Position Check": instance.label_position_check,
        # "Label Position Photo": instance.label_position_check_evidence.url if instance.label_position_check_evidence else "",
        "Visual Handset Appearance Check": instance.visual_inspection_handset,
        "Logo Check": instance.logo_check,
        # "Logo Photo": instance.logo_check_evidence.url if instance.logo_check_evidence else "",
        "Battery Assembly Check": instance.assembly_battery_check,
        # "Battery Assembly Photo": instance.assembly_battery_check_evidence.url if instance.assembly_battery_check_evidence else "",
        "Net Color Check": instance.net_color_check,
        "TP Key Function Check": instance.tp_with_key_check,
        "Screw Check": instance.screw_check,
        "TP Charge Test": instance.tp_with_charge_test,
        "15-Min Charge Test": instance.charge_15min_test,
        "Boot Time Test": instance.boot_time_test,
        # "Boot Time Evidence": instance.boot_time_test_evidence.url if instance.boot_time_test_evidence else "",
        "Initialization & Settings Test": instance.init_settings_test,
        "Button & Key Feel Test": instance.buttons_keys_test,
        "Touch Screen Pen Test": instance.touch_screen_pen_test,
        "Calling Test": instance.calling_test,
        "Bluetooth Function Test": instance.bluetooth_test,
        "Flashlight/Induction Test": instance.flashlight_test,
        "Camera Flash Test": instance.camera_flash_test,
        "Front/Rear Camera Test": instance.camera_photo_test,
        # "Front Camera Photo": instance.camera_front_test_evidence.url if instance.camera_front_test_evidence else "",
        # "Rear Camera Photo": instance.camera_back_test_evidence.url if instance.camera_back_test_evidence else "",
        "Camera Dark Test": instance.camera_dark_test,
        # "Camera Dark Photo": instance.camera_dark_test_evidence.url if instance.camera_dark_test_evidence else "",
        "Long Distance Camera Check": instance.camera_long_distance_check,
        "High Light Defect Check": instance.highlight_defect_check,
        "Multimedia Play Test": instance.multimedia_play_test,
        "FM Play Test": instance.fm_play_test,
        "TV Function Test": instance.tv_fn_test,
        "Taping Function Test": instance.taping_fn_test,
        "Shaking Screen Test": instance.shaking_screen_test,
        "WiFi Function Test": instance.wifi_test,
        "Gravity Sensor Test": instance.gravity_sensor_test,
        "Light & Distance Sensor Test": instance.light_distance_sensor_test,
        "Hall Function Test": instance.hall_fn_test,
        "QR Code Scan Test": instance.qr_scan_test,
        "RAM/ROM/T Card Capacity Test": instance.ram_rom_cap_test,
        "Mode Switch Test": instance.mode_switch_test,
        "Touch in Developer Options Test": instance.touch_in_dev_opt_test,
        "MAC Address Check": instance.mac_add_test,
        "OTG Function Test": instance.otg_fn_test,
        "T-Card/SIM Plug-Pull Test": instance.tcard_sim_plug_test,
        "Auto Focus Clarity Test": instance.focus_test,
        "Front/Back Camera Photo Test": instance.front_back_cam_test,
        "Slight Drop Test": instance.slight_drop_test,
        "Charging & USB Stability Test": instance.slight_touch_test,
        "Coupling RF Test": instance.coumpling_rf_test,
        "Power Consumption Test": instance.power_consumption_test,
        "High Temperature Simulation Test": instance.high_temp_simul_test,
        "Post Factory Reset Function Test": instance.factory_reset_fn_test,
        "SAR Value Test": instance.sar_value_test,
        "Post Factory Reset Call Noise Test": instance.factory_reset_call_noise_test,
        "Factory Reset Visual Test": instance.factory_reset_test,
        "High Temp Boot Test": instance.high_temp_boot_check,
        "High Temp Engineering Mode Test": instance.high_temp_engi_mode_test,
        "High Temp Call Test": instance.high_temp_call_test,
        "High Temp Charging Test": instance.high_temp_charging_test,
        "High Temp Camera Test": instance.high_temp_camera_test,
        "High Temp Camera Photo": instance.high_temp_camera_test_evidence.url if instance.high_temp_camera_test_evidence else "",
        "Shutdown Behavior Test": instance.shutdown_test,
        "Sample Serial Number": instance.sample_serial_number,
        "IMEI Number": instance.imei_number,
        # "IMEI Photo": instance.imei_photo.url if instance.imei_photo else "",
        "Visual & Functional Result": instance.visual_functional_result,
        "Reliability Test Result": instance.reliability_result,
        # "Inspector Name": instance.inspector_name or "",
        # "QE Confirm Name": instance.qe_confirm_name or "",
        # "QE Confirm Status": instance.qe_confirm_status or "",
        "Public Token": str(instance.public_token),
        "Remarks": instance.remarks,
        # "Public URL": {"link": instance.public_url} if instance.public_url else None,
        # "Created At": date_to_ms(instance.created_at),
        # "Updated At": date_to_ms(instance.updated_at),
    }


    payload = {"fields": fields}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json={"fields": fields})
    res_json = response.json()
    if response.status_code == 200 and res_json.get("code") == 0:
        print("✅ Synced successfully to Bitable.")
    else:
        print(f"⚠️ Sync failed: {res_json}")
        
        
def update_testing_fai_in_bitable(instance):
    """Update existing record in Lark Bitable based on Public Token"""
    token = get_lark_access_token()
    if not token:
        print("❌ No access token, skipping update.")
        return False

    table_id = getattr(settings, "LARK_TABLE_TESTING_FAI", None)
    if not table_id:
        print("❌ Table ID missing in settings.")
        return False

    app_token = getattr(settings, "LARK_BITABLE_APP_TOKEN_QA", None)
    url = f"https://open.larkoffice.com/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"

    headers = {"Authorization": f"Bearer {token}"}

    # ✅ Step 1: Fetch all records from table
    res = requests.get(url, headers=headers)
    data = res.json()

    if data.get("code") != 0:
        print("⚠️ Failed to fetch records:", data)
        return False

    records = data.get("data", {}).get("items", [])
    public_token = str(instance.public_token).strip()

    # ✅ Step 2: Find matching record in Bitable
    matching_record = None
    for record in records:
        bitable_token = str(record.get("fields", {}).get("Public Token", "")).strip()
        if bitable_token == public_token:
            matching_record = record
            break

    if not matching_record:
        print(f"⚠️ No matching record found in Bitable for token: {public_token}")
        return False

    record_id = matching_record.get("record_id")
    if not record_id:
        print("⚠️ Record ID missing in matching record.")
        return False

    # ✅ Step 3: Update QE fields
    update_fields = {
        "QE Confirm Name": instance.qe_confirm_name or "",
        "QE Confirm Status": instance.qe_confirm_status or "",
        "Public URL": instance.public_url or "",
    }

    update_url = f"{url}/{record_id}"
    update_res = requests.put(
        update_url,
        headers={**headers, "Content-Type": "application/json"},
        json={"fields": update_fields},
    )

    update_data = update_res.json()
    if update_data.get("code") == 0:
        print(f"✅ Updated QE fields successfully in Bitable for token: {public_token}")
        return True
    else:
        print(f"⚠️ Failed to update QE fields in Bitable: {update_data}")
        return False