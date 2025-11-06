from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
import os
import uuid

# class IPQCWorkInfo(models.Model):
    
#     SHIFT_CHOICES = [
#         ('Day', 'Day'),
#         ('Night', 'Night'),
#     ]
    
#     date = models.DateField()
#     shift = models.CharField(max_length=20, choices=SHIFT_CHOICES)
#     emp_id = models.CharField(max_length=20)
#     name = models.CharField(max_length=100)
#     section = models.CharField(max_length=50)
#     line = models.CharField(max_length=20)
#     group = models.CharField(max_length=20)
#     model = models.CharField(max_length=50)
#     color = models.CharField(max_length=50)
#     created_at = models.DateTimeField(default=timezone.now)

#     def __str__(self):
#         return f"{self.date} - {self.emp_id} - {self.model}"
    
#     def save(self, *args, **kwargs):
#         if not self.created_at:
#             self.created_at = timezone.now()
#         super().save(*args, **kwargs)

class IPQCWorkInfo(models.Model):
    
    SHIFT_CHOICES = [
        ('Day', 'Day'),
        ('Night', 'Night'),
    ]
    
    SECTION_CHOICES = [
        ('Assembly', 'Assembly'),
        ('NT', 'NT'),
        ('SMT', 'SMT'),
    ]
    
    emp_id = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateField()
    shift = models.CharField(max_length=20)
    section = models.CharField(max_length=50)
    line = models.CharField(max_length=50)
    group = models.CharField(max_length=50)
    model = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date} - {self.emp_id} - {self.model})"
        
        
        
        
FIELD_TYPES = [
    ('text', 'Text'),
    ('number', 'Number'),
    ('date', 'Date'),
    ('select', 'Select'),
    ('checkbox', 'Checkbox'),
]

class DynamicForm(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    lark_bitable_table_id = models.CharField(max_length=200)  # Table ID to sync
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class DynamicFormField(models.Model):
    form = models.ForeignKey(DynamicForm, on_delete=models.CASCADE, related_name="fields")
    label = models.CharField(max_length=200)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    required = models.BooleanField(default=True)
    options = models.TextField(blank=True, null=True)  # comma separated for select fields
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.form.title} - {self.label}"


class DynamicFormSubmission(models.Model):
    form = models.ForeignKey(DynamicForm, on_delete=models.CASCADE)
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    data = models.JSONField()  # store submitted values
    created_at = models.DateTimeField(auto_now_add=True)

# Define the choices for the audit fields
AUDIT_CHOICES = [
    ('OK', 'OK'),
    ('NOT_OK', 'Not OK'),
    ('NA', 'NA'),
]
 
class  IPQCAssemblyAudit(models. Model):
    # Basic Info
    date = models. DateField(default=timezone.now, verbose_name="Date")
    shift = models. CharField(max_length=50, verbose_name="Shift", blank=True, null=True)
    name = models. CharField(max_length=100, verbose_name="IPQC Name", blank=True, null=True)
    emp_id = models. CharField(max_length=50, verbose_name="Employee ID", blank=True, null=True)
    section = models. CharField(max_length=100, verbose_name="Section", blank=True, null=True)
    group = models. CharField(max_length=100, verbose_name="Group", blank=True, null=True)
    line = models. CharField(max_length=100, verbose_name="Line", blank=True, null=True)
    model = models. CharField(max_length=100, verbose_name="Model", blank=True, null=True)
    color = models. CharField(max_length=50, default="Unknown", verbose_name="Colour", blank=True, null=True)
    created_at = models. DateTimeField(auto_now_add=True)
        
        # MAN
    man_job_card = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="Check the key stations for one time per shift whether the operator job card is available or not, if not then operator will be considered as a new operator, need to focus his its operation and the results.")
    man_btb_mon = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="For install BTB station, IPQC monitor guideline/SOP as: In the Every 2Hrs, IPQC check these stations operator new or change , if no change Check 5-Device after BTB Buckling/Bending stage and Also Check BTB Buckling/Bending Process of operator on 5-devices, if have been changed/New, need check 10 device after BTB buckling/Bending and also check his process. Also Monitor in FAI devices and TRC repair devices and also Monitor to TRC Operator.")
    
        # MACHINE
    mach_epa_check = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="In all EPA areas, check the antistatic clothing, caps and slipper of the operators wear well. Check that all stations requiring electrostatic protection are wearing electrostatic wrist bands / electrostatic gloves/Finger coat / Good grounding of Equipments, computers, electric iron, Manual screw driver etc.")
        # ... Add choices=AUDIT_CHOICES to all fields from man_job_card to auto_screw_sample ...
    mach_screw_torque = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="Check screw driver torque right or not, must less 0.9kgf/cm2/According To SOP. All Manual Screw Driver Hang In Spring Blancer And Hight Of Screw Bit Is 4CM From The Working Table And Always Manual screw Driver Hang On Flip Cover Side Of The Jigs. <b>Also Soldering Temperature must as per SOP standard.</b>")
    mach_light = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="The Light illuminance of the CTQ Stages.The illuminance of the inspection station should match to the document requirements. (800 - 1200 Lux)")
    mach_fixture_clean = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="There is no foreign body and obvious dirty in the fixture/Machine, especially pay attention to check the BTB pressing , Camera Lens pressing, Window lens pressing , Battery pressing & Automatic screw machine the working face must not have dirty, foreign body And After All jigs/Fixtures,  Machine/pressing Jigs/Equipment/Soldering Station Check 5 Sample & Check Visual Inspection.")
    mach_jig_label = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="The model on the jig lable is match the actual model, fixture maintenance labels in the validity period.")
    mach_teflon = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="The teflon adhesive paper pasted on the fixture shall not be raised, creased or damaged.")
    mach_press_params = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="The presure & time of pressing jig within the range or not?")
    mach_glue_params = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="The parameter of glueing machine, glueing route, glueing weight, glueing dispersion effect, whether meet the requirement? <b>(Glue Machine alignment should be proper from that glue directly go inside the PCBA hole, As per SOP)</b>")
    mach_eq_move_notify = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="When find the vary of equipment, jig, tool on line, or the equipment have been moved, changed, or maintenanced should inform to PQE.")
    mach_feeler_gauge = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="Every shift 2 times (morning and afternoon) IPQC check FQC Feeler gauge condition ok or not")
    mach_hot_cold_press = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="Check the parameter of temperature,time,pressure for hot press station/cold press station.")
    mach_ion_fan = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="The ion fan should face to operation area, within 30-40 cm from work station.")
    mach_cleanroom_eq = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="Check Clean room RTI, PAL, Audio, Current Test, All Pressing stages, IMEI Write / IMEI Check, WBG, Antenna Test etc. equipment maintenance same as per the requirement or not. Also verify the checksheet of all these stages are filled properly or not.")
    mach_rti_check = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="RTI: Information of computer check, Manufacture: (Check printed QR code same as BOM (Color, SN), Check there should not repeted SN (5 Pcs at a time), QR Code print is OK or NOT. Check the Software Description should be match with BOM, if any change inform to PQC Engineer/PQE.)")
    mach_current_test = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name=")Current Tester: Check the Test item/Parameters standard. Parameters should be same in all the system. Check Upper Limt and Lower Limit of items/Parameters match with the standard. Check Test station have the Defect label and Area or not.")
    mach_pal_qr = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="PAL: Service QR code is OK or Not. (Check the Print of QR), Check the Test item/Parameters standard. Parameters should be same in all the system, SN No match the QR Code or not. (Check there should not repeated QR, 5 Pcs at a time).")
    mach_auto_screw = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="Automatic Screwing: Check the teaching of the machine is as per the SOP or not, check on sampling base, there should not screw miss / loose by machine (5pcs per hr). Check the Screw according to BOM (Color, Quantity etc.)")
    
        # MATERIAL
    mat_key_check = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="Key materials are checked one time every 2 hours, including: Main board, LCM, FPC, Camera, Receiver, Speaker, Motor, Fingerprint module, Battery,Battery Cover, All Label . Other materials random sampling to check, but need to ensure that check once every shift for all materials.")
    mat_special_stop = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="If have a special document required to stop one material (including suspension of date code, material code, material batch, supplier's material, module number, etc.), need to check whether the production line has stopped to use.")
    mat_improved_monitor = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="When find the improved material / concession materials /Deviation Material be fed to line, need monitor the production follow the document and feedback to PQE.")
    mat_result_check = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="Randomly check on the operation result of using the materials correctly, and the assembly results are correct; All supported materials (cushion / tape / cotton / PET /mylar etc.) should be flat, no shift, no lift,No missing etc. No screw missing issue and loose issue. 5pcs at a time.")
    mat_battery_issue = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="When find the battery issue of leakage liquid, smoking, burning etc. must inform PQE immediately.")
    mat_ipa_check = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="Check the use of IPA on the production line in accordance with the document requirements (0.5 ml for remove battery / Clean PCBA). Check the container to have a clear label.")
    mat_thermal_gel = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="Check the use of Thermal Conductive Gel Weight (the amount of glue in gram) on the production line with the help of Glue Weight Machine in accordance with the document or model requirements, (such as 0.28+0.03g ), Check the dispensing position,route,path, direction is correct,")
    mat_verification = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="Verify the Material: Match with Bom / SOP / Physically (Nautral part-code), Also verify the process as per the Location and Quantity mentioned in SOP and BOM.")
    
        # METHOD
    meth_sop_seq = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="Verify the Sequence of the SOP, Check the operation manual,There should not be lack of process, whether operator working according to that or not. Check the tools, and units mentioned in SOP also the availability online.")
    meth_distance_sensor = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="Verify the Distance Sensor Jig Hight should be 2.25 CM range or not.")
    meth_rear_camera = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="Verify the rear camera Seal / cushion after battery cover installation station and after repaired devices in TRC area.")
    meth_material_handling = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="In the process of transportation, storage, operation, unpacking, the material of identification, placement, stacking height , Pending, Handling and others whether according to the requirements of the document.")
    meth_guideline_doc = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="When operation need guideline document, Production guide, SOP, OPL, the document need to be hung within valid period; need to timely return the document which is invalid/ no need for current model.")
    meth_operation_doc = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="All operations on lines should be carried out as per the documents, mail notice, on-site guidance. Can not follow oral notice and can not privately splitting, merging, exchanging, omission, or changing document.")
    meth_defective_feedback = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="If IPQC find defective Products / Process Skip should feedback to PQE for confirmation. When PQE judges need to segregate to rework, IPQC should supervise the production line to mark and segregate the materials, semi-finished product and finished products in a specific area, and follow up the rework of risk product.")
    meth_line_record = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="Verify that the production line report / check sheet is correctly recorded of required stations, Operation of the Equipment is ok or not.")
    meth_no_self_repair = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="No self-repair of Device / Equipment / Modification of fixture by production person.")
    meth_battery_fix = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="For the inbuilt battery model, should monitor whether the battery fix properly before install battery cover on line.")
    meth_line_change = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="For production line change model, or new line start, should verificate all materials in 3 Hrs of beginning; and check the material of old model have been cleaned out.")
    meth_trail_run = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="When there have trail run material order / New line/ New Model start on line, IPQC need monitor 4M1E and prepare Line readyness check sheet, and get more 5 pcs samples to check. Inform PQE at the same time .")
    meth_dummy_conduct = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="Conduct Dummy for Key stages, Also Machine Dummy & Manpower Dummy on daily basis / If any Machine change / after breakdown / any manpower change online / new manpower / top defect online etc. Conduct dummy for the concern issues. Also as per the defect found in Seg-2 / OQC, conduct dummy for the same issue online.")
    
        # ENVIRONMENT
    env_prod_monitor = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="Every shift 2 times (morning and afternoon) IPQC monitor the production environment the temperature, humidity and others match the requirement of production environment or not; The temperature of the production environment is controlled at 16℃ / 28℃ (the Aging room should not exceed 30℃), and the relative humidity is controlled at 45% - 75%.")
    env_5s = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="Check the 5's requirment (Sort, Set in order, Shine, Standardize, Sustain) of Assembly line / Area, meets the standard.")
    
        # TRC / FAI / DEFECT / SPOT CHECK
    trc_flow_chart = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="Check whether Flow Chart available or not. Randomly check the defect entry of any device to verify whether entry in MES or not, Operator working as per the flow chart or not. Check 5's and handling should be maintained at TRC station.")
    fai_check = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="Check the First Article Inspection of the shift: 1) Do the functional and Appearance of the device, 2) Also verify the material as per the BOM & SOP, 3) Check the S/W version / SAR Value, Labels, Specially check Demo video, BIS, Extra applications / All functional test,  files etc.as per the document of FAI.")
    defect_monitor = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="Check the key inspection station (Function, Appearance) defect devices have record or not, Check the defect rate is beyond the limit or not.")
    spot_check = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="Random selection of the disassemble main board / semi-finished product, to confirm whether they already finished entry MES (Online and TRC).")
    auto_screw_sample = models. CharField(max_length=200, blank=True, null=True, choices=AUDIT_CHOICES, verbose_name="Each hour IPQC must check 4 samples Automatic Screwing, Before Seg-1 stage & RQC stage, in order to avoid battery cover impression mark & screw dent or any Appreance defect.")
    
        # Manual Input Fields
    manufacture = models. CharField(max_length=100, blank=True, null=True)
    work_order = models. CharField(max_length=100, blank=True, null=True)
    brand = models. CharField(max_length=50, blank=True, null=True)
    material_code = models. CharField(max_length=50, blank=True, null=True)
    wo_input_qty = models. IntegerField(blank=True, null=True, verbose_name="WO / Input Qty")
    
        # TOP 3 DEFECTS & REMARKS
    top3_defects = models. CharField(max_length=200, blank=True, null=True, verbose_name="Top 3 defects")
    remarks = models. TextField(blank=True, null=True, verbose_name="Remarks")
    
        # Signatures
    ipqc_sign = models. CharField(max_length=100, blank=True, null=True, verbose_name="IPQC Sign")
    pqe_tl_sign = models. CharField(max_length=100, blank=True, null=True, verbose_name="PQE/TL Sign")
    
    def __str__(self):
        return f"{self.model} - {self.date} - {self.emp_id}"
    
    
    
    
    
class  BTBFitmentChecksheet(models. Model):
    # --- Header Information ---
    date = models.DateField(verbose_name="Date")
    shift = models.CharField(max_length=20, verbose_name="Shift")
    emp_id = models.CharField(max_length=20, verbose_name="Employee ID")
    name = models.CharField(max_length=100, verbose_name="Employee Name")
    line = models.CharField(max_length=20, verbose_name="Line")
    group = models.CharField(max_length=20, verbose_name="Group")
    model = models.CharField(max_length=50, verbose_name="Model")
    color = models.CharField(max_length=50, verbose_name="Colour")
    frequency = models. CharField(max_length=50, default="Per Hour", verbose_name="Frequency")
    created_by = models. ForeignKey(
    settings. AUTH_USER_MODEL, 
    on_delete=models. CASCADE, 
            verbose_name="Submitted By"
        )
    created_at = models. DateTimeField(auto_now_add=True)
    
        # --- Data Grid Fields ---
        
    # CAM BTB
    input_9 = models. IntegerField(default=0, verbose_name="Input - 9:00")
    input_10 = models. IntegerField(default=0, verbose_name="Input - 10:00")
    input_11 = models. IntegerField(default=0, verbose_name="Input - 11:00")
    input_12 = models. IntegerField(default=0, verbose_name="Input - 12:00")
    input_1 = models. IntegerField(default=0, verbose_name="Input - 1:00")
    input_2 = models. IntegerField(default=0, verbose_name="Input - 2:00")
    input_3 = models. IntegerField(default=0, verbose_name="Input - 3:00")
    input_4 = models. IntegerField(default=0, verbose_name="Input - 4:00")
    input_5 = models. IntegerField(default=0, verbose_name="Input - 5:00")
    input_6 = models. IntegerField(default=0, verbose_name="Input - 6:00")
    input_total = models. IntegerField(default=0, verbose_name="Input - Total", editable=False)
    
    
        # CAM BTB
    cam_btb_9 = models. IntegerField(default=0, verbose_name="CAM BTB - 9:00")
    cam_btb_10 = models. IntegerField(default=0, verbose_name="CAM BTB - 10:00")
    cam_btb_11 = models. IntegerField(default=0, verbose_name="CAM BTB - 11:00")
    cam_btb_12 = models. IntegerField(default=0, verbose_name="CAM BTB - 12:00")
    cam_btb_1 = models. IntegerField(default=0, verbose_name="CAM BTB - 1:00")
    cam_btb_2 = models. IntegerField(default=0, verbose_name="CAM BTB - 2:00")
    cam_btb_3 = models. IntegerField(default=0, verbose_name="CAM BTB - 3:00")
    cam_btb_4 = models. IntegerField(default=0, verbose_name="CAM BTB - 4:00")
    cam_btb_5 = models. IntegerField(default=0, verbose_name="CAM BTB - 5:00")
    cam_btb_6 = models. IntegerField(default=0, verbose_name="CAM BTB - 6:00")
    cam_btb_total = models. IntegerField(default=0, verbose_name="CAM BTB - Total", editable=False)
    
        # LCD Fitment
    lcd_fitment_9 = models. IntegerField(default=0, verbose_name="LCD Fitment - 9:00")
    lcd_fitment_10 = models. IntegerField(default=0, verbose_name="LCD Fitment - 10:00")
    lcd_fitment_11 = models. IntegerField(default=0, verbose_name="LCD Fitment - 11:00")
    lcd_fitment_12 = models. IntegerField(default=0, verbose_name="LCD Fitment - 12:00")
    lcd_fitment_1 = models. IntegerField(default=0, verbose_name="LCD Fitment - 1:00")
    lcd_fitment_2 = models. IntegerField(default=0, verbose_name="LCD Fitment - 2:00")
    lcd_fitment_3 = models. IntegerField(default=0, verbose_name="LCD Fitment - 3:00")
    lcd_fitment_4 = models. IntegerField(default=0, verbose_name="LCD Fitment - 4:00")
    lcd_fitment_5 = models. IntegerField(default=0, verbose_name="LCD Fitment - 5:00")
    lcd_fitment_6 = models. IntegerField(default=0, verbose_name="LCD Fitment - 6:00")
    lcd_fitment_total = models. IntegerField(default=0, verbose_name="LCD Fitment - Total", editable=False)
    
        # MAIN FPC
    main_fpc_9 = models. IntegerField(default=0, verbose_name="MAIN FPC - 9:00")
    main_fpc_10 = models. IntegerField(default=0, verbose_name="MAIN FPC - 10:00")
    main_fpc_11 = models. IntegerField(default=0, verbose_name="MAIN FPC - 11:00")
    main_fpc_12 = models. IntegerField(default=0, verbose_name="MAIN FPC - 12:00")
    main_fpc_1 = models. IntegerField(default=0, verbose_name="MAIN FPC - 1:00")
    main_fpc_2 = models. IntegerField(default=0, verbose_name="MAIN FPC - 2:00")
    main_fpc_3 = models. IntegerField(default=0, verbose_name="MAIN FPC - 3:00")
    main_fpc_4 = models. IntegerField(default=0, verbose_name="MAIN FPC - 4:00")
    main_fpc_5 = models. IntegerField(default=0, verbose_name="MAIN FPC - 5:00")
    main_fpc_6 = models. IntegerField(default=0, verbose_name="MAIN FPC - 6:00")
    main_fpc_total = models. IntegerField(default=0, verbose_name="MAIN FPC - Total", editable=False)
        
        # Battery
    battery_9 = models. IntegerField(default=0, verbose_name="Battery - 9:00")
    battery_10 = models. IntegerField(default=0, verbose_name="Battery - 10:00")
    battery_11 = models. IntegerField(default=0, verbose_name="Battery - 11:00")
    battery_12 = models. IntegerField(default=0, verbose_name="Battery - 12:00")
    battery_1 = models. IntegerField(default=0, verbose_name="Battery - 1:00")
    battery_2 = models. IntegerField(default=0, verbose_name="Battery - 2:00")
    battery_3 = models. IntegerField(default=0, verbose_name="Battery - 3:00")
    battery_4 = models. IntegerField(default=0, verbose_name="Battery - 4:00")
    battery_5 = models. IntegerField(default=0, verbose_name="Battery - 5:00")
    battery_6 = models. IntegerField(default=0, verbose_name="Battery - 6:00")
    battery_total = models. IntegerField(default=0, verbose_name="Battery - Total", editable=False)
    
        # Finger Printer
    finger_printer_9 = models. IntegerField(default=0, verbose_name="Finger Printer - 9:00")
    finger_printer_10 = models. IntegerField(default=0, verbose_name="Finger Printer - 10:00")
    finger_printer_11 = models. IntegerField(default=0, verbose_name="Finger Printer - 11:00")
    finger_printer_12 = models. IntegerField(default=0, verbose_name="Finger Printer - 12:00")
    finger_printer_1 = models. IntegerField(default=0, verbose_name="Finger Printer - 1:00")
    finger_printer_2 = models. IntegerField(default=0, verbose_name="Finger Printer - 2:00")
    finger_printer_3 = models. IntegerField(default=0, verbose_name="Finger Printer - 3:00")
    finger_printer_4 = models. IntegerField(default=0, verbose_name="Finger Printer - 4:00")
    finger_printer_5 = models. IntegerField(default=0, verbose_name="Finger Printer - 5:00")
    finger_printer_6 = models. IntegerField(default=0, verbose_name="Finger Printer - 6:00")
    finger_printer_total = models. IntegerField(default=0, verbose_name="Finger Printer - Total", editable=False)
    
        # --- Row Totals (Calculated) ---
    total_9 = models. IntegerField(default=0, verbose_name="Total - 9:00", editable=False)
    total_10 = models. IntegerField(default=0, verbose_name="Total - 10:00", editable=False)
    total_11 = models. IntegerField(default=0, verbose_name="Total - 11:00", editable=False)
    total_12 = models. IntegerField(default=0, verbose_name="Total - 12:00", editable=False)
    total_1 = models. IntegerField(default=0, verbose_name="Total - 1:00", editable=False)
    total_2 = models. IntegerField(default=0, verbose_name="Total - 2:00", editable=False)
    total_3 = models. IntegerField(default=0, verbose_name="Total - 3:00", editable=False)
    total_4 = models. IntegerField(default=0, verbose_name="Total - 4:00", editable=False)
    total_5 = models. IntegerField(default=0, verbose_name="Total - 5:00", editable=False)
    total_6 = models. IntegerField(default=0, verbose_name="Total - 6:00", editable=False)
        
        # --- Grand Total (Calculated) ---
    
    remark_input = models.TextField(blank=True, null=True, verbose_name="Remark - Input")
    remark_cam_btb = models.TextField(blank=True, null=True, verbose_name="Remark - CAM BTB")
    remark_lcd_fitment = models.TextField(blank=True, null=True, verbose_name="Remark - LCD Fitment")
    remark_main_fpc = models.TextField(blank=True, null=True, verbose_name="Remark - MAIN FPC")
    remark_battery = models.TextField(blank=True, null=True, verbose_name="Remark - Battery")
    remark_finger_printer = models.TextField(blank=True, null=True, verbose_name="Remark - Finger Printer")

    grand_total = models. IntegerField(default=0, verbose_name="Grand Total", editable=False)
    
    def __str__(self):
        return f"{self.model} - {self.date}"

    def save(self, *args, **kwargs):
        # Safely convert to int (treat None or '' as 0)
        def safe_int(val):
            try:
                return int(val or 0)
            except (TypeError, ValueError):
                return 0

        # --- Column Totals (Exclude Input) ---
        self.cam_btb_total = sum([safe_int(getattr(self, f'cam_btb_{h}')) for h in [9,10,11,12,1,2,3,4,5,6]])
        self.lcd_fitment_total = sum([safe_int(getattr(self, f'lcd_fitment_{h}')) for h in [9,10,11,12,1,2,3,4,5,6]])
        self.main_fpc_total = sum([safe_int(getattr(self, f'main_fpc_{h}')) for h in [9,10,11,12,1,2,3,4,5,6]])
        self.battery_total = sum([safe_int(getattr(self, f'battery_{h}')) for h in [9,10,11,12,1,2,3,4,5,6]])
        self.finger_printer_total = sum([safe_int(getattr(self, f'finger_printer_{h}')) for h in [9,10,11,12,1,2,3,4,5,6]])

        # --- Input Total (Separate) ---
        self.input_total = sum([safe_int(getattr(self, f'input_{h}')) for h in [9,10,11,12,1,2,3,4,5,6]])

        # --- Row Totals (Sum all defect columns only, exclude input if you want) ---
        for h in [9,10,11,12,1,2,3,4,5,6]:
            setattr(self, f'total_{h}', 
                    safe_int(getattr(self, f'cam_btb_{h}')) 
                + safe_int(getattr(self, f'lcd_fitment_{h}'))
                + safe_int(getattr(self, f'main_fpc_{h}'))
                + safe_int(getattr(self, f'battery_{h}'))
                + safe_int(getattr(self, f'finger_printer_{h}'))
            )

        # --- Grand Total (Exclude Input) ---
        self.grand_total = (
            self.cam_btb_total
            + self.lcd_fitment_total
            + self.main_fpc_total
            + self.battery_total
            + self.finger_printer_total
        )

        super().save(*args, **kwargs)
        
        
class AssDummyTest(models.Model):
    date = models.DateField()
    shift = models.CharField(max_length=50)
    emp_id = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    section = models.CharField(max_length=100)        # <-- Must exist
    line = models.CharField(max_length=100)
    group = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    test_stage = models.CharField(max_length=100)
    test_item = models.CharField(max_length=200)
    operator_name = models.CharField(max_length=100)
    operator_id = models.CharField(max_length=50)
    
    RESULT_CHOICES = [
        ('Pass', 'Pass'),
        ('Fail', 'Fail'),
        ('NA', 'NA'),
    ]
    result = models.CharField(max_length=10, choices=RESULT_CHOICES)
    
    cause = models.TextField(blank=True, null=True)
    measure = models.TextField(blank=True, null=True)
    ll_confirm = models.TextField(default=False)
    remark = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.date} - {self.line} - {self.group} - {self.test_item}"
    
    
class IPQCDisassembleCheckList(models.Model):
    
    FORM_CHOICES = [
        ('OK', 'OK'),
        ('Not OK', 'Not OK'),
        ('NA', 'NA'),
    ]

    # --- Work Info ---
    date = models.DateField(verbose_name="Date")
    shift = models.CharField(max_length=10, verbose_name="Shift")
    emp_id = models.CharField(max_length=20, verbose_name="Employee ID")
    name = models.CharField(max_length=100, verbose_name="Employee Name")
    section = models.CharField(max_length=100, verbose_name="Section")
    line = models.CharField(max_length=100, verbose_name="Line")
    group = models.CharField(max_length=100, verbose_name="Group")
    model = models.CharField(max_length=100, verbose_name="Model")
    color = models.CharField(max_length=50, verbose_name="Color")

    # --- Appearance / Assembly Quality ---
    color_match = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Color matches reference or not")
    color_match_photo = models.ImageField(upload_to='ipqc_disassemble/color_match/', blank=True, null=True)

    cam_lens_assembly = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Camera lens assembled correctly")
    cam_lens_cleanliness = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Camera lens clean (no dust/fingerprint)")
    cam_lens_photo = models.ImageField(upload_to='ipqc_disassemble/camera_lens/', blank=True, null=True)

    key_feel = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Key hand feeling OK")
    key_alignment = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Keys aligned and no tilt or gap")
    key_photo = models.ImageField(upload_to='ipqc_disassemble/keys/', blank=True, null=True)

    screw_missing = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="All screws present (no missing)")
    screw_loose = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="No loose screws")
    screw_spec = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Screw specification correct")
    screw_photo = models.ImageField(upload_to='ipqc_disassemble/screw/', blank=True, null=True)

    front_housing_damage = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Front housing damage/scratch/gap or not")
    back_housing_damage = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Back housing damage/scratch/gap or not")
    housing_snap_fit = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Front/back housing snap joints fitted properly")
    housing_photo = models.ImageField(upload_to='ipqc_disassemble/housing/', blank=True, null=True)

    proof_label_position = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Waterproof label positioned correctly")
    proof_label_photo = models.ImageField(upload_to='ipqc_disassemble/proof_label/', blank=True, null=True)

    # --- Assembly as per SOP ---
    tp_sop = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Touch Panel assembled as per SOP")
    mic_solder = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Mic soldering as per SOP")
    led_solder = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="LED soldering as per SOP")
    lcd_stick = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="LCD sticking/soldering as per SOP")
    speaker_solder = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Speaker soldering as per SOP")
    motor_solder = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Motor soldering as per SOP")
    key_solder = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Key soldering as per SOP")
    sim_subboard_solder = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="SIM sub-board soldering as per SOP")
    subboard_solder = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Subboard soldering as per SOP")
    camera_solder = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Camera soldering as per SOP")
    receiver_solder = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Receiver soldering as per SOP")

    # --- Component & Connection Check ---
    coaxial_line = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Coaxial line assembled correctly")
    antenna_shrapnel = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Mainboard antenna shrapnel OK")
    antenna_fpc = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Antenna FPC assembled properly")
    conductive_fabric = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Conductive fabric positioned as per SOP")
    insulation_paste = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Insulation paste positioned correctly")
    ins_paste_cover = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Insulation paste fully covers all pins")

    lcd_fpc_defect = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="LCD FPC indentation/scald or not")
    tp_fpc_defect = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="TP FPC indentation/scald or not")
    key_fpc_solder = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Key FPC soldering OK")
    keypad_defect = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Keypad FPC has no burn/indentation")

    mainboard_component_ok = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Mainboard all components OK")

    solder_splash = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="No solder splash or foreign material inside device")
    foam_stick = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Foam stick positioned correctly")
    cam_glue = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Camera back glue not torn off")
    led_position = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="LED centered correctly")

    # --- Glue / Fixture Validation ---
    jig_fixture_test = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Jig/fixture impression test done & verified glue activation")
    glue_location = models.CharField(max_length=10, choices=FORM_CHOICES, verbose_name="Thermal/battery/deco glue on correct location")
    glue_weight_1 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Measured glue weight pcs 1 (g)")
    glue_weight_2 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Measured glue weight pcs 2 (g)")
    glue_weight_3 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Measured glue weight pcs 3 (g)")

    # --- Validation Photos ---
    assembly_overview_photo = models.ImageField(upload_to='ipqc_disassemble/overview/', blank=True, null=True)
    defect_photo = models.ImageField(upload_to='ipqc_disassemble/defects/', blank=True, null=True)

    # --- IMEI & Remarks ---
    imei1 = models.CharField(max_length=20, blank=True, null=True, verbose_name="IMEI 1")
    imei2 = models.CharField(max_length=20, blank=True, null=True, verbose_name="IMEI 2")
    defect_cause = models.TextField(blank=True, null=True, verbose_name="Defect Cause Analysis / Remark")
    pqe = models.CharField(max_length=100, blank=True, null=True, verbose_name="PQE")
    pe = models.CharField(max_length=100, blank=True, null=True, verbose_name="PE")
    apd_ll = models.CharField(max_length=100, blank=True, null=True, verbose_name="APD LL")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.date} - {self.model} - {self.name}"

class NCIssueTracking(models.Model):
    # --- Work Info (existing fields) ---
    date = models.DateField(verbose_name="Date")
    shift = models.CharField(max_length=10, verbose_name="Shift")
    emp_id = models.CharField(max_length=20, verbose_name="Employee ID")
    name = models.CharField(max_length=100, verbose_name="Employee Name")
    section = models.CharField(max_length=100, verbose_name="Section")
    line = models.CharField(max_length=100, verbose_name="Line")
    group = models.CharField(max_length=100, verbose_name="Group")
    model = models.CharField(max_length=100, verbose_name="Model")
    color = models.CharField(max_length=50, verbose_name="Color")

    # --- Issue Tracking Fields ---
    stage = models.CharField(max_length=100, verbose_name="Stage")
    time = models.DateTimeField(verbose_name="Time of Issue")  
    issue = models.TextField(verbose_name="Issue")
    three_why = models.TextField(verbose_name="3 Why")
    solution = models.TextField(verbose_name="Solution")
    operator_name = models.CharField(max_length=100, verbose_name="Operator Name")
    operator_id = models.CharField(max_length=50, verbose_name="Operator ID")
    responsible_dept = models.CharField(max_length=100, verbose_name="Responsible Dept.")
    responsible_person = models.CharField(max_length=100, verbose_name="Responsible Person")
    close_time = models.DateTimeField(verbose_name="Close Time", blank=True, null=True)
    status = models.CharField(max_length=50, verbose_name="Status")
    remark = models.TextField(verbose_name="Remark", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.date} - {self.model} - {self.issue[:20]}"

from django.db import models

AUDIT_CHOICES = [
    ('YES', 'Yes'),
    ('NO', 'No'),
    ('NA', 'Not Applicable'),
]

SHIFT_CHOICES = [
    ('Day', 'Day'),
    ('Night', 'Night'),
]

class ESDComplianceChecklist(models.Model):
    date = models.DateField(verbose_name="Date")
    shift = models.CharField(max_length=10, choices=SHIFT_CHOICES, verbose_name="Shift")
    emp_id = models.CharField(max_length=20, verbose_name="Employee ID")
    name = models.CharField(max_length=100, verbose_name="Employee Name")
    line = models.CharField(max_length=100, verbose_name="Line")
    group = models.CharField(max_length=100, verbose_name="Group")
    model = models.CharField(max_length=100, verbose_name="Model")
    color = models.CharField(max_length=50, verbose_name="Color")

    # --- ESD Compliance Checklist ---

    # 1. Clothing Rules
    epa_clothes = models.CharField(max_length=10, choices=AUDIT_CHOICES, default='NA', verbose_name="Enter EPA must wear ESD clothes")
    epa_clothes_photo = models.ImageField(upload_to='esd_audit/clothes/', blank=True, null=True, verbose_name="Photo Evidence - ESD Clothes")

    forbid_wear_out = models.CharField(max_length=10, choices=AUDIT_CHOICES, default='NA', verbose_name="Forbid to wear ESD clothes out of workshop")
    no_accessories = models.CharField(max_length=10, choices=AUDIT_CHOICES, default='NA', verbose_name="Accessories not allowed on ESD clothes")

    clothes_clean = models.CharField(max_length=10, choices=AUDIT_CHOICES, default='NA', verbose_name="ESD clothes should be clean and tidy")

    collar_cover = models.CharField(max_length=10, choices=AUDIT_CHOICES, default='NA', verbose_name="Non-ESD collar not allowed to cover ESD clothes")
    all_buttons_closed = models.CharField(max_length=10, choices=AUDIT_CHOICES, default='NA', verbose_name="All buttons of ESD clothes should be buckled")
    clothes_length = models.CharField(max_length=10, choices=AUDIT_CHOICES, default='NA', verbose_name="Non-ESD clothes should not be longer than ESD clothes")
    watch_expose = models.CharField(max_length=10, choices=AUDIT_CHOICES, default='NA', verbose_name="Watch or accessories should not be exposed")

    hair_cap = models.CharField(max_length=10, choices=AUDIT_CHOICES, default='NA', verbose_name="Hair should not be exposed outside ESD cap")
    hair_cap_photo = models.ImageField(upload_to='esd_audit/haircap/', blank=True, null=True, verbose_name="Photo Evidence - ESD Cap")

    # 2. Wristband and Slipper
    slipper_check = models.CharField(max_length=10, choices=AUDIT_CHOICES, default='NA', verbose_name="Daily check ESD slipper")
    wristband_check = models.CharField(max_length=10, choices=AUDIT_CHOICES, default='NA', verbose_name="Daily check ESD wrist band")
    pre_line_check = models.CharField(max_length=10, choices=AUDIT_CHOICES, default='NA', verbose_name="Before line start, check if wrist band works")
    wrist_touch_skin = models.CharField(max_length=10, choices=AUDIT_CHOICES, default='NA', verbose_name="Wrist band should touch skin fully")
    wristband_photo = models.ImageField(upload_to='esd_audit/wristband/', blank=True, null=True, verbose_name="Photo Evidence - Wrist Band Check")

    # 3. Handling Rules
    no_touch_pcba = models.CharField(max_length=10, choices=AUDIT_CHOICES, default='NA', verbose_name="Not allowed to touch PCBA/PCB or ESDS without protection")
    alert_plug_out = models.CharField(max_length=10, choices=AUDIT_CHOICES, default='NA', verbose_name="Alert should trigger when ESD wristband unplugged")

    # 4. Grounding and Equipment
    trolley_grounding = models.CharField(max_length=10, choices=AUDIT_CHOICES, default='NA', verbose_name="All trolleys should have grounding cable")
    trolley_photo = models.ImageField(upload_to='esd_audit/trolley/', blank=True, null=True, verbose_name="Photo Evidence - Trolley Grounding")

    device_grounded = models.CharField(max_length=10, choices=AUDIT_CHOICES, default='NA', verbose_name="All electronic devices grounded properly")
    grounding_points_tight = models.CharField(max_length=10, choices=AUDIT_CHOICES, default='NA', verbose_name="Grounding points tight and secure")

    ion_fan_distance = models.CharField(max_length=10, choices=AUDIT_CHOICES, default='NA', verbose_name="Ion fan distance > 30cm from ESDS")
    ion_fan_direction = models.CharField(max_length=10, choices=AUDIT_CHOICES, default='NA', verbose_name="Ion fan directed towards ESDS/PCBA")
    ion_fan_photo = models.ImageField(upload_to='esd_audit/ionfan/', blank=True, null=True, verbose_name="Photo Evidence - Ion Fan Setup")

    # 5. Consumables
    gloves_condition = models.CharField(max_length=10, choices=AUDIT_CHOICES, default='NA', verbose_name="Gloves/finger coats not broken or dirty")
    mat_grounded = models.CharField(max_length=10, choices=AUDIT_CHOICES, default='NA', verbose_name="ESD mat grounded and within effective date")
    mat_photo = models.ImageField(upload_to='esd_audit/mat/', blank=True, null=True, verbose_name="Photo Evidence - ESD Mat")

    audit_label_valid = models.CharField(max_length=10, choices=AUDIT_CHOICES, default='NA', verbose_name="All ESD audit labels within effective date")

    # 6. Material Handling
    esds_box = models.CharField(max_length=10, choices=AUDIT_CHOICES, default='NA', verbose_name="All ESDS stored in ESD box/transportation box")
    table_no_source = models.CharField(max_length=10, choices=AUDIT_CHOICES, default='NA', verbose_name="Working table has no ESD source within 30cm of ESDS/PCBA")
    table_photo = models.ImageField(upload_to='esd_audit/table/', blank=True, null=True, verbose_name="Photo Evidence - Working Table")

    # 7. Tools & Environment
    tools_audit = models.CharField(max_length=10, choices=AUDIT_CHOICES, default='NA', verbose_name="Hot air gun and soldering iron audited daily")
    temp_humidity = models.CharField(max_length=10, choices=AUDIT_CHOICES, default='NA', verbose_name="Temperature and humidity within SPEC")
    tray_voltage = models.CharField(max_length=10, choices=AUDIT_CHOICES, default='NA', verbose_name="Friction voltage for tray < ±100V")

    # Environmental readings
    temperature_value = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Actual Temperature (°C)")
    humidity_value = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Actual Humidity (%)")
    tray_voltage_value = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Measured Tray Voltage (V)")

    # Remarks and Tracking
    remark = models.TextField(verbose_name="Remarks", blank=True, null=True)
    photo_overview = models.ImageField(upload_to='esd_audit/overview/', blank=True, null=True, verbose_name="Overview Photo for Spot Validation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.date} - {self.line} - {self.name}"



class DustCountCheck(models.Model):
    date = models.DateField(verbose_name="Date")
    shift = models.CharField(max_length=10, verbose_name="Shift")
    emp_id = models.CharField(max_length=20, verbose_name="Employee ID")
    name = models.CharField(max_length=100, verbose_name="Employee Name")
    line = models.CharField(max_length=100, verbose_name="Line")
    group = models.CharField(max_length=100, verbose_name="Group")
    model = models.CharField(max_length=100, verbose_name="Model")
    color = models.CharField(max_length=50, verbose_name="Color")
    
    # Measurements in particles per cubic meter (or as appropriate)
    micrometer_0_3 = models.PositiveIntegerField(verbose_name="≥0.3 micrometer")
    micrometer_0_5 = models.PositiveIntegerField(verbose_name="≥0.5 micrometer")
    micrometer_1_0 = models.PositiveIntegerField(verbose_name="≥1.0 micrometer")
    
    checked_by = models.CharField(max_length=100, verbose_name="Checked By")
    verified_by = models.CharField(max_length=100, verbose_name="Verified By")
    
    remark = models.TextField(verbose_name="Remarks", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.date} - Checked: {self.checked_by} - Verified: {self.verified_by}"
    

# --- Choice options ---
FORM_RESULT_CHOICES = [
    ('MEET_REQ', 'Meet Requirement'),
    ('QUALIFIED', 'Qualified'),
    ('UNQUALIFIED', 'Unqualified'),
    ('CONDITIONAL_ACC', 'Conditional Acceptance'),
]

FORM_CHOICES = [
    ('OK', 'OK'),
    ('Not OK', 'Not OK'),
    ('NA', 'Not Applicable'),
]

FORM_APPROVAL = [
    ('APPROVED', 'Approved'),
    ('REJECTED', 'Rejected'),
    ('PENDING', 'Pending'),
]

# First article actual situation choices
FAI_SITUATION_CHOICES = [
    ('NORMAL_WORK_ORDER_PROD', 'Normal work order production'),
    ('CHANGE_LINE', 'Change line'),
    ('MODEL_CHANGE', 'Change model'),
    ('CHANGE_MATERIAL', 'Change color/material/software'),
    ('PROD_RETURN_NORMAL', 'Production return to normal after abnormal'),
    ('SPECIAL_OR_REWORK_ORDER', 'Special or rework order'),
]

def fai_evidence_upload_path(instance, filename):
    """Generate unique path for FAI evidence files"""
    return os.path.join(
        'fai_evidence', 
        f"{instance.id}_{instance.model_color}_{timezone.now().strftime('%Y%m%d')}_{filename}"
    )

class  TestingFirstArticleInspection(models. Model):
    """
    Comprehensive First Article Inspection (FAI) model with all inspection criteria
    and evidence management for visual, functional, and reliability checks.
    """
    
    class Meta: # <--- ONLY ONE Meta class
        db_table = 'ipqc_testing_first_article_inspection'
        verbose_name = "First Article Inspection"
        verbose_name_plural = "First Article Inspections"
        ordering = ['-date', '-created_at']
 
    # --- Core Information ---
    date = models. DateField(verbose_name="Date")
    shift = models. CharField(max_length=10, verbose_name="Shift")
    emp_id = models. CharField(max_length=20, verbose_name="Employee ID")
    name = models. CharField(max_length=100, verbose_name="Employee Name")
    section = models. CharField(max_length=100, verbose_name="Section")
    line = models. CharField(max_length=100, verbose_name="Line")
    group = models. CharField(max_length=100, verbose_name="Group")
    model = models. CharField(max_length=100, verbose_name="Model")
    color = models. CharField(max_length=50, verbose_name="Color")
        
        # --- Production Info ---
    production_work_order_no = models. CharField(max_length=100, verbose_name="Production Work Order No.")
    first_article_type = models. CharField(max_length=100, choices=FAI_SITUATION_CHOICES, verbose_name="First Article Type")
        
        # --- Order & Software Checks ---
    software_ver_check = models. CharField(max_length=20, verbose_name="Check if software version is the latest version")
    android_ver_check = models. CharField(max_length=20, verbose_name="Check if OS version is the latest version")
    memory_inbuilt_check = models. CharField(max_length=20, choices=FORM_CHOICES, verbose_name="Result")
    order_confirm_check = models. CharField(max_length=20, choices=FORM_CHOICES, verbose_name="Confirm if inspection information is consistent with actual shipment requirements")
        
        # --- Labels Checks ---
    label_check = models. CharField(max_length=20, choices=FORM_CHOICES, verbose_name="check with BOM list ,if there's missing, pasted in wrong place etc")
    label_check_evidence = models. ImageField(upload_to='fai/label/', blank=True, null=True, verbose_name="Label Photo")
    label_position_check = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Label position should meet the requirements of the SOP ")
    label_position_check_evidence = models. ImageField(upload_to='fai/label/', blank=True, null=True, verbose_name="Position Photo")
        
        # --- Visual Inspection ---
    visual_inspection_handset = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Visual Handset Appearance Check")
    logo_check = models. TextField(max_length=100, choices=FORM_CHOICES, verbose_name="Logo Check is right or not")
    logo_check_evidence = models. ImageField(upload_to='fai/visual/', blank=True, null=True, verbose_name="Logo Photo")
    assembly_battery_check = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Assembly of battery cover/surface shell/bottom case has no segment difference and is not too tight or loose")
    assembly_battery_check_evidence = models. ImageField(upload_to='fai/visual/', blank=True, null=True, verbose_name="Assembly Photo")
    net_color_check = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Check if there is net cover with the handset and its colour is consistent")
    tp_with_key_check = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Press the top, bottom, left, right, receiver, menu key of TP, check if the TP is defective")
    screw_check = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Check if there's screw missing or untigtened")
        
        # --- Functional Tests ---
    tp_with_charge_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="No TP drift or display abnormality during charger on/off.")
    charge_15min_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Actual 15min Charging Test")
    boot_time_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Boot Bright Screen Time Test (<2s)")
    boot_time_test_evidence = models. ImageField(upload_to='fai/function/', blank=True, null=True, verbose_name="Boot time evidence image")
    init_settings_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Initialization Settings & Function Test")
    buttons_keys_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Buttons/Side Keys Feel Test")
    touch_screen_pen_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Touch Screen Pen/Drift Test")
    calling_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Calling Test (with/without earphone)")
        
        # --- Additional Functions ---
    bluetooth_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Bluetooth Function Test")
    flashlight_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Flashlight/Induction Lamp Test")
    camera_flash_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Photo flash is normal")
    camera_photo_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Front/Rear Camera Photo Test")
    camera_front_test_evidence = models. ImageField(upload_to='fai/camera/', blank=True, null=True, verbose_name="Front Camera Photo Evidence")
    camera_back_test_evidence = models. ImageField(upload_to='fai/camera/', blank=True, null=True, verbose_name="Back Camera Photo Evidence")
    camera_dark_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Camera in Dark Condition Test")
    camera_dark_test_evidence = models. ImageField(upload_to='fai/camera/', blank=True, null=True, verbose_name="Dark Condition Photo")
    camera_long_distance_check = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Long Distance (8W:50cm; 30W:60cm; 200W FF:3m; 500W+:3–5m)")
    highlight_defect_check = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="High-Light (800–1200Lux) – Check White Screen, Exposure, Distortion")
        
        # --- Multimedia test & Other special function test  ---
    multimedia_play_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Can play MP3, MP4 normally")
    fm_play_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Can search & play FM normally")
    tv_fn_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="TV function is normal")
    taping_fn_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Taping function is normal")
    shaking_screen_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Shaking screen function is normal")
    wifi_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="WIFI function is normal")
    gravity_sensor_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Gravity sensor function is normal")
    light_distance_sensor_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Light sensor, distance sensor function is normal")
    hall_fn_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Hall function is normal")
    qr_scan_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="QR code test, Scane the QR code and check should be same with device SN")
    ram_rom_cap_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="check if T card capacity，RAM capacity， ROM capacity are normal")
    mode_switch_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Different mode can be switch normally")
    touch_in_dev_opt_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Touch test in Developer options")
    mac_add_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Check MAC address")
    otg_fn_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="OTG function is normal")
        
        # --- Reliability Test ---
    tcard_sim_plug_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="T-Card/SIM Plug/Pull Test (10 cycles)")
    focus_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Auto-focus clarity test at ≥10 cm distance")
    front_back_cam_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Front/Back camera photo test (10 shots each)")
    slight_drop_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Slight Drop Test (7 cm, 6 sides × 20 drops = 120; no cover loss, call/power stable, no paint damage)")
    slight_touch_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Charging function & USB port stability test (touch 5×, no charge breaks)")
    coumpling_rf_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="“GSM900/1800 power & interference test (CMD55, call/touch/earphone check)")
    power_consumption_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Power Consumption Test (standby, startup, BT, vibration, backlight, MP3/MP4 with dual SIM)")
    high_temp_simul_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="High temperature simulation test: Half-day batches tested by IPQC; issues retested and reported to PQE, who alerts departments and stops the line if needed")
    factory_reset_fn_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Post- factory reset function check – photo, video, BT, download")
    sar_value_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="*SAR value check via #07# and device manual")
    factory_reset_call_noise_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Post- factory reset check Call interface key noise and sound quality test")
    factory_reset_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Test model, select 'factory reset', input '234', click 'ENTER', reset handset and do the visual inspection.")
        
        # --- High Temperature Tests ---
    high_temp_boot_check = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Boot-up test (4× total, 2× with & 2× without battery; check display after high-temp)")
    high_temp_engi_mode_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name=" The engineering model test content completely")
    high_temp_call_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Call function test (dial 198, check connection, receiver & mic sound quality)")
    high_temp_charging_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="Post-chamber charging test (verify charging function & battery display)")
    high_temp_camera_test = models. CharField(max_length=100, choices=FORM_CHOICES, verbose_name="High Temp Camera Test: Camera function test (front/rear preview, capture, flash, album browse & delete)")
    high_temp_camera_test_evidence = models. ImageField(upload_to='fai/temp/', blank=True, null=True, verbose_name="Camera Test Photo")
        
        # --- Final Results ---
    shutdown_test = models. CharField(max_length=100, verbose_name="Check if it shutdown under user guide interface after production line restore factory settings ")
    sample_serial_number = models. CharField(max_length=100, verbose_name="Sample Serial Number")
    imei_number = models. CharField(max_length=100, verbose_name="IMEI Number")
    imei_photo = models. ImageField(upload_to='fai/sample/', blank=True, null=True, verbose_name="IMEI Verification Photo")
    visual_functional_result = models. CharField(max_length=30, choices=FORM_RESULT_CHOICES, verbose_name="Visual & Functional Test Result")
    reliability_result = models. CharField(max_length=30, choices=FORM_RESULT_CHOICES, verbose_name="Reliability Test Result")
    inspector_name = models. CharField(max_length=100, blank=True, null=True, verbose_name="Inspector Name")
    qe_confirm_name = models. CharField(max_length=100, blank=True, null=True, verbose_name="QE Confirm Name")
    qe_confirm_status = models. CharField(max_length=100, choices=FORM_APPROVAL, blank=True, null=True, verbose_name="QE Confirm Status")
    
    public_token = models. UUIDField(default=uuid.uuid4, unique=True, editable=False)
    public_url = models. URLField(max_length=255, null=True, blank=True)
    remarks = models. TextField(blank=True, null=True, verbose_name="Remarks")
    created_at = models. DateTimeField(auto_now_add=True)
    updated_at = models. DateTimeField(auto_now=True)
 
    def __str__(self):
        return f"FAI: {self.date} - {self.emp_id} - {self.model}"
    
    def get_public_url(self, request=None):
        """Generates the absolute public URL for QE confirmation."""
        from django.urls import reverse
        # Use the public update URL name
        path = reverse('testing_fai_public_update', args=[str(self.public_token)])
        return request.build_absolute_uri(path) if request else path

class OperatorQualificationCheck(models.Model):
    JOB_CARD_STATUS = [
        ('Have', 'Have'),
        ('Not Have', 'NO'),
        ('NA', 'Not Applicable'),
    ]
    TRAINING_STATUS = [
        ('Done', 'Done'),
        ('Pending', 'Pending'),
        ('NA', 'Not Applicable'),
    ]
    OPERATOR_STATUS = [
        ('Old', 'Old'),
        ('New', 'New'),
        ('Rotating', 'Rotating'),
    ]
    PQE_INFO_STATUS = [
        ('Training Pending', 'Training Pending'),
        ('Already Done', 'Already Done'),
        ('Replace Operator', 'Replace Operator'),
    ]
    PQE_TRAINING_STATUS = [
        ('Done', 'Done'),
        ('Training Pending', 'Training Pending'),
        ('Already Done', 'Already Done'),
        ('Replace Operator', 'Replace Operator'),
    ]
    OPERATOR_QUALIFICATION = [
        ('Trained', 'Trained'),
        ('Not Trained', 'Not Trained'),
        ('Replace Operator', 'Replace Operator'),
    ]
    
    # Basic Information
    emp_id = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateField()
    shift = models.CharField(max_length=20)
    section = models.CharField(max_length=50)
    line = models.CharField(max_length=50)
    group = models.CharField(max_length=50)
    model = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    
    # Job Card Scanning
    key_station_name = models.TextField(verbose_name="Select/Write the key station Name")
    key_station_job_card_status = models.CharField(max_length=50, choices=JOB_CARD_STATUS, verbose_name="Check whether the key station operator has a job card, if not, it is considered a new operator")
    scanned_barcode_image = models.ImageField(upload_to='ipqc/manpower/barcode_scans/', blank=True, null=True, verbose_name="Optional scan snapshot (image)", help_text="Image captured during scanning, optional")
    scanned_barcode_text = models.URLField(max_length=500, blank=True, null=True, verbose_name="Scanned Job Card URL", help_text="Auto-filled from barcode scan")
    
    # Verification Fields
    key_station_operator_status = models.CharField(max_length=50, choices=OPERATOR_STATUS, verbose_name="Select Key station operator status: old/new/rotating operator")
    new_or_rotating_operator_status = models.CharField(max_length=50, choices=PQE_INFO_STATUS, verbose_name="IPQC monitoring for new or rotating operators at specific stations (e.g., BTB, TRC)")
    check_operator_work_instruction = models.CharField(max_length=50, choices=OPERATOR_QUALIFICATION, verbose_name="Check whether the operator has a work instruction, if not, it is considered a new operator, and the PQE should be notified for training")
    operator_job_card_image = models.ImageField(upload_to='ipqc/manpower/jobcard/', blank=True, null=True, verbose_name="Upload operator job card image for record")
    pqe_training_and_verification_status = models.CharField(max_length=50, choices=PQE_TRAINING_STATUS, verbose_name="Summary: PQE training and verification process (5 cycles, 5 samples, Dummy test)")
    job_card_verification_summary = models.TextField(verbose_name="Summary: Verify operator job card; if missing, monitor and perform Dummy test")

    created_at = models.DateTimeField(auto_now_add=True)
    feishu_record_data = models.JSONField(blank=True, null=True, verbose_name="Feishu Record Data")
    
    class Meta:
        verbose_name = "Operator Qualification Procedure"
        verbose_name_plural = "Operator Qualification Procedures"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.date} - {self.emp_id} - {self.model}"









from django.db.models.signals import post_save
from django.dispatch import receiver
from .services import sync_btb_fitment_to_bitable, sync_dummy_test_to_bitable, sync_dessembly_checklist_to_bitable, sync_ipqc_assembly_audit_to_bitable, sync_nc_issue_tracking_to_bitable, sync_esd_compliance_to_bitable, sync_dust_measurement_to_bitable, sync_testing_fai_to_bitable, update_testing_fai_in_bitable

@receiver(post_save, sender=BTBFitmentChecksheet)
def sync_to_bitable_after_save(sender, instance, created, **kwargs):
    if created:
        sync_btb_fitment_to_bitable(instance)
           
@receiver(post_save, sender=AssDummyTest)
def sync_to_bitable_after_save(sender, instance, created, **kwargs):
    if created:
        sync_dummy_test_to_bitable(instance)
        
@receiver(post_save, sender=IPQCDisassembleCheckList)
def sync_to_bitable_after_save(sender, instance, created, **kwargs):
    if created:
        sync_dessembly_checklist_to_bitable(instance)

@receiver(post_save, sender=IPQCAssemblyAudit)
def sync_to_bitable_after_save(sender, instance, created, **kwargs):
    if created:
        sync_ipqc_assembly_audit_to_bitable(instance)

@receiver(post_save, sender=NCIssueTracking)
def sync_to_bitable_after_save(sender, instance, created, **kwargs):
    if created:
        sync_nc_issue_tracking_to_bitable(instance)

@receiver(post_save, sender=ESDComplianceChecklist)
def sync_to_bitable_after_save(sender, instance, created, **kwargs):
    if created:
        sync_esd_compliance_to_bitable(instance)

@receiver(post_save, sender=DustCountCheck)
def sync_to_bitable_after_save(sender, instance, created, **kwargs):
    if created:
        sync_dust_measurement_to_bitable(instance)
        
@receiver(post_save, sender=TestingFirstArticleInspection)
def sync_to_bitable_after_save(sender, instance, created, **kwargs):
    """Sync to Lark Bitable after save"""
    if created:
        # Create new record in Bitable when a new FAI record is created
        sync_testing_fai_to_bitable(instance)
    else:
        # Update existing record when QE updates public fields
        update_testing_fai_in_bitable(instance)
        
        
        
        
