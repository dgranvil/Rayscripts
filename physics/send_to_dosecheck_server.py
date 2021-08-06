# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 09:16:03 2021
ToDo:
create a function that exports the plan to dqa
split this script into segments

@author: bywilson
"""
from connect import *
from datetime import datetime
class physics_QA:
    def __init__(self):
        
        self.plan = get_current('Plan')
        self.case = get_current('Case')
        self.beamset = get_current('BeamSet')
        self.patient = get_current("Patient")
        self.isApproved = self.plan.Review.ApprovalStatus == 'Approved'
        if not self.isApproved:
            raise Exception('Plan Not approved') 
        self.tomo_machines =  ['T_TomoTherapy_1', 'T_TomoTherapy_2']
        self.isTomo =self.beamset.MachineReference.MachineName in self.tomo_machines
        self.TPCT = self.beamset.PatientSetup.OfTreatmentSetup.PatientSetup.LocalizationPoiGeometrySource.OnExamination.Name
        self.warnings = []
        self.Testing = True 
        
    def do_task(self):
        
        self.create_isodose_contours()
            
        self.export_to_R_and_V()
        self.create_DQA()
        
        if self.isTomo:
            self.create_transferred_tomo_plan()
        # self.create_plan_document()
        self.SNC_dose_calc()
        self.physics_checks()
        self.print_warnings()
        
    def do_QC(self):
        self.physics_checks()
        self.print_warnings()
        
    def print_warnings(self):
        for m in self.warnings:
            print(m)
            
        
        
    def export_to_R_and_V(self):
        if self.isApproved:
            
            planning_exam =self.TPCT
            if self.isTomo:
                self.case.ScriptableDicomExport(RayGatewayTitle = 'RayGateway',
                                                Examinations = [planning_exam],
                                                RtStructureSetsForExaminations = [planning_exam],
                                                BeamSets = [self.beamset.BeamSetIdentifier()],
                                                BeamSetDoseForBeamSets =[self.beamset.BeamSetIdentifier()],
                                                IgnorePreConditionWarnings = self.Testing)
                 
            else:
                self.case.ScriptableDicomExport(Connection = { 'Title' : 'IMPAC_DCM_SCP' },
                                                Examinations = [planning_exam],
                                                RtStructureSetsForExaminations = [planning_exam],
                                                BeamSets = [self.beamset.BeamSetIdentifier()],
                                                IgnorePreConditionWarnings = self.Testing)
        else:
            raise Exception('Plan Not approved') 
            # self.warnings.append('plan not exported to R&V because not approved')
            
    
    def create_plan_document(self):
        
        # self.plan.TreatmentCourse.TotalDose.UpdateDoseGridStructures()
        # file_name = 'I:\raystation_test_doc.pdf'
       
        
        # # Access the first template for a plan report in the clinic database
        # # clinic_db = get_current('ClinicDB')
        # # site_settings = clinic_db.GetSiteSettings()
        # # template =  next(t for t in site_settings.ReportTemplates if t.Type == 'TreatmentPlanReport')
        # # template_name = template.Name
        # template_name = 'RayStation treatment plan report'
        
        # try:
        #     # Try to create report, do not ignore warnings
        #     self.beamset.CreateReport(templateName = template_name, filename = file_name, ignoreWarnings = False)
        
        # except (System.InvalidOperationException, SystemError) as e:
    
        #     # Display the warnings to the user
        #     print ('Someting went wrong: {0}'.format(e))
        #     print ('Retry and ignore warnings.')
        
        #     # Create report, ignore warnings
        #     self.beamset.CreateReport(templateName = template_name, filename = file_name, ignoreWarnings = True)
        
        self.beamset.CreateReport(templateName = 'CompositePlanReport10A',
                                    filename = 'I:\raystation_test_2232.pdf',
                                    ignoreWarnings = True)
            
        
    def create_isodose_contours(self):

        ROIs = self.case.PatientModel.RegionsOfInterest
        prescription_doses = set()
        for ROI in ROIs:
            if ROI.Type == 'Ptv' or 'ptv' in ROI.Name.lower():
                N = self.find_dose_from_PTV_name(ROI.Name)
                if N != None:
                    prescription_doses.add(N)


        dose_distribution = self.beamset.FractionDose
        Colours = ['Orange','Red','Blue','White']
        ROINames = [ROI.Name for ROI in ROIs]
        for i, D in enumerate(prescription_doses):
            D95= D*0.95
            ##Check whether ROI has been created first
            isodose_ROI_name = 'Isodose_%dcGy'%D95
            if  isodose_ROI_name in ROINames:
                ROI = ROIs[isodose_ROI_name]
                
            else:
                ROI = self.case.PatientModel.CreateRoi(Name = isodose_ROI_name, Type = 'Control',Color = Colours[i%len(Colours)])
            ROI.CreateRoiGeometryFromDose(DoseDistribution= self.plan.TreatmentCourse.TotalDose, ThresholdLevel=D95)
        
        self.patient.Save()
    def create_transferred_tomo_plan(self):
        #Look to see whether case has the transferred plan
        new_plan_name = self.plan.Name + '_Transferred'
        for plan_i in self.case.TreatmentPlans:
            if plan_i.Name == new_plan_name:
                self.warnings.append('Transferred plan already exists, did not create')
                return
            
        
        patient = self.patient
        tomo_machines =self.tomo_machines
        current_machine = self.beamset.MachineReference.MachineName
        otherMachine = next(i for i in tomo_machines if i!= current_machine)
        self.patient.Save()
        self.case.CopyAndAdjustTomoPlanToNewMachine(PlanName=self.plan.Name,
                                            NewMachineName=otherMachine,
                                            OnlyCopyAndChangeMachine=False)
        
        self.patient.Save()
        ##Bug, might not work if ran twice.
        newplan = self.case.TreatmentPlans[self.plan.Name+'_Transferred']
        for b in newplan.BeamSets:
            b.ComputeDose(DoseAlgorithm='CCDose')
        
        self.patient.Save()
        ##Add in system wait to make sure that the plan is good?
        new_beam_set = newplan.BeamSets[0]
        # # ##send to machine
        # # beam_set_transferred = get_current("BeamSet") #Need to get new, becuase its just been created
        # # original_beam_set_identifier = 
        prev_beam_set_identifier = self.beamset.BeamSetIdentifier()
        ui = get_current('ui')
        ui.TitleBar.MenuItem['Plan evaluation'].Button_Plan_evaluation.Click()
        await_user_input('Please Verify that backup plan is suitable, and that primary plan is approved in IDMS')
        # new_beam_set = self.beamset
        new_beam_set.SendTransferredPlanToRayGateway(RayGatewayTitle="RayGateway", 
                                                 PreviousBeamSet = prev_beam_set_identifier,
                                                 OriginalBeamSet = prev_beam_set_identifier,
                                                 IgnorePreConditionWarnings=True)
    def create_DQA(self):
        ##Create DQA
        
        beamset = self.beamset
        current_machine = beamset.MachineReference.MachineName
        tomo_machines = self.tomo_machines
        if current_machine in tomo_machines:
            #DQA phantom with tomo couch
            phantom_name = r"TomoD4v1 TomoD4v1"
            phantom_id =  r"TomoD4v1"
            
        else:
            #DQA phantom with elekta couch
            phantom_name = r"DELTA4OZ"
            phantom_id = r"DELTA4OZ"
        QA_plan_name =self.get_unique_QA_plan_name()
        
        
        #Tomo and ELekta have different couch models, so D4 have different models
        beamset.CreateQAPlan(PhantomName=phantom_name, PhantomId=phantom_id,
                              QAPlanName=QA_plan_name, 
                              IsoCenter={ 'x': -0.13, 'y': 10.11, 'z': 0.1 },
                              DoseGrid={ 'x': 0.2, 'y': 0.2, 'z': 0.2 }, 
                              GantryAngle=None, CollimatorAngle=None, 
                              CouchRotationAngle=None, 
                              ComputeDoseWhenPlanIsCreated=True,
                              NumberOfMonteCarloHistories=None, 
                              MotionSynchronizationTechniqueSettings={ 'DisplayName': None, 'MotionSynchronizationSettings': None, 'RespiratoryIntervalTime': None, 'RespiratoryPhaseGatingDutyCycleTimePercentage': None },
                              RemoveCompensators=False, EnableDynamicTracking=False)
        
        ui = get_current('ui')
        ui.TitleBar.MenuItem['QA preparation'].Button_QA_preparation.Click()
        await_user_input('Please Verify that verification plan is good')
        
        #Send the plan to the appropriate place -> need to add justins server thing
        created_plan = next(P for P in self.plan.VerificationPlans if P.BeamSet.DicomPlanLabel == QA_plan_name)
        if created_plan.BeamSet.FractionDose.BeamDoses[0].DoseAtPoint== None:
            created_plan.BeamSet.ComputeDose(ComputeBeamDoses=True, DoseAlgorithm="CCDose", ForceRecompute=True)
        
        self.patient.Save()

        ##print plan doc of DQA for shifts?

        ##ToDO need to get justins server to add a tag for gantry rotation period
        created_plan.ScriptableQADicomExport(Connection = {'Title' : 'PYNETDICOM' },ExportBeamSet = True, ExportBeamSetDose=True,ExportBeamSetBeamDose = True)

    
       
    def get_unique_QA_plan_name(self):
        existing_plan_names = [P.BeamSet.DicomPlanLabel for P in self.plan.VerificationPlans]
        name_candidate0 = 'D4QA'
        name_candidate = name_candidate0
        i = 0
        while name_candidate in existing_plan_names:
            name_candidate = name_candidate0 + str(i)
            i+=1

        return name_candidate

    def is_tomo_treatment(self):
        current_machine = self.beamset.MachineReference.MachineName
        return current_machine in ['T_TomoTherapy_1', 'T_TomoTherapy_2']
    
    def SNC_dose_calc(self):
        #send the plan to SNC
        patient = self.patient
        
        patient.Save()

        if self.isApproved:
            planning_exam =self.beamset.PatientSetup.OfTreatmentSetup.PatientSetup.LocalizationPoiGeometrySource.OnExamination.Name
            
            self.case.ScriptableDicomExport(Connection = { 'Title' : 'SunNuclear_SCP' },
                                       Examinations = [planning_exam],
                                       RtStructureSetsForExaminations = [planning_exam],
                                       BeamSets = [self.beamset.BeamSetIdentifier()],
                                       IgnorePreConditionWarnings = self.Testing)
        else:
            self.warnings.append('plan not exported to SunNuclear because not approved')
        
        return -1

    def physics_checks(self):
        #check whether beam model is correct comissioning time
        
        commissioned_machines = ['ElektaVersaHD 2/9/2021 2:10:03 PM',
                                 'T_TomoTherapy_1 9/29/2020 9:14:00 AM',
                                 'T_TomoTherapy_2 9/29/2020 9:42:05 AM']
        unique_machine_name = self.beamset.MachineReference.MachineName+' ' + self.beamset.MachineReference.CommissioningTime.__str__()
        
        if not unique_machine_name in commissioned_machines:
            self.warnings.append('Beam model does not match comissioned machines')
            
        #Check whether the TPCT has a valid RED curve
            
        comissioned_CT_machines = ['HOST-7055 12/9/2020 3:12:08 PM',
                                   'HOST-76205 12/9/2020 3:51:16 PM',
                                   'PHILIPS-7055 1/8/2020 2:33:32 PM']
        TPCT = self.case.Examinations[self.TPCT]
        TPCT_reference = TPCT.EquipmentInfo.ImagingSystemReference
        unique_CT_machine_name = TPCT_reference.ImagingSystemName + " " + TPCT_reference.CommissioningTime.__str__()
        
        if not unique_CT_machine_name in comissioned_CT_machines:
            self.warnings.append('CT-RED curve does not match comissioned machines')
        
        if self.beamset.ModificationInfo.SoftwareVersion != '10.0.1.52':
            self.warnings.append('Wrong Raystation software version')
        
        #Check whether energy is correct for VMAT
        if not self.is_tomo_treatment():
            for beam in self.beamset.Beams:
                if beam.DeliveryTechnique == 'DynamicArc' and beam.BeamQualityId != '6':
                    self.warnings.append('VMAT beam %s not a comissioned energy' %beam.Name )
        
        #make sure that voxel spacing is approriate 2mm or less
        for direction in 'xyz':
            if self.beamset.FractionDose.InDoseGrid.VoxelSize[direction]>0.2:
                self.warnings.append('dose voxel size greater than 2mm')
        
        
        #Make sure that the correctcouch is applied for the treatment unit
        self.check_couch()
       
    
    def check_couch(self):
         #make sure that couch is correct for treatment machine.
        ROI_names = [ROI.Name for ROI in self.case.PatientModel.RegionsOfInterest]
        if self.isTomo:
            couch_structures = ['Couch Top', 'Couch Inner', 'Couch Ribbon', 'Base Exterior', 'Base Interior']
        else: 
            couch_structures = ['ElektaCouch']
            
        if sum([c in ROI_names for c in couch_structures]) != len(couch_structures):
            self.warnings.append('Couch top may be wrong or incomplete')


    def find_dose_from_PTV_name(self, PTV_name):
    
        s = '' 
        nums = set()
        
        for c in PTV_name:
            if c.isnumeric():
                s= s+c
            else:
                if len(s):
                    nums.add(int(s))
                s = ''
        if len(s):
            nums.add(int(s))
            
        for n in nums:
            if n >100 and n <10000: #suitable range
                return n
        else:
            return None

def do_task(**options):
    physics_QA().SNC_dose_calc()
    


