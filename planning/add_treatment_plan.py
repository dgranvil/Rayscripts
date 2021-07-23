# -*- coding: utf-8 -*-
"""
Created on Tue Apr 13 11:24:11 2021
##Tested on cpython 3.6
@author: bywilson

Bug: add in check to see whether course exists and create unique name if it does
"""
from connect import *
from collections import defaultdict


class add_treatment_plan :
    def __init__(self, course_number = 1, machine_name = 'ElektaVersaHD', number_of_fx = 1):
        ##init things
        
        self.patient = get_current('Patient')
        self.db = get_current("PatientDB")
        self.case = get_current('Case')
        
        self.course_number = course_number
        self.exam = get_current('Examination')
        
        
        # self.treatment_machines = [r'ElektaVersaHD', r"T_TomoTherapy_1",  r"T_TomoTherapy_2" ]
        self.machine_name = machine_name
        
        if machine_name == 'ElektaVersaHD':
            self.treatment_technique = 'VMAT'
        else:
            self.treatment_technique = "TomoHelical"
        
        self.assign_prescription_ROI()
       
        
        self.num_fractions = number_of_fx
        self.warnings = []
        
        
    def do_task(self):
        ##create beam
        # self.check_for_couch()
        
        self.add_treatment_plan()
        
        self.add_treatment_beams()
        # self.apply_clinical_goals()
        # self.add_optimization_functions()
        # self.run_optimization()
        
        print(self.warnings)
      
    def assign_prescription_ROI(self):
        '''Find the prescription ROI based on which has the highest dose
        assigned to it. Return the dose and ROI name'''
        
        ROIs = self.case.PatientModel.RegionsOfInterest
        prescription_doses = defaultdict(list)
        for ROI in ROIs:
            if ROI.Type == 'Ptv' or 'ptv' in ROI.Name.lower():
                N = self.find_dose_from_PTV_name(ROI.Name)
                if N != None:
                    prescription_doses[N].append(ROI.Name)
        self.prescription_dose = max(prescription_doses.keys())
        
        
        ROIs = prescription_doses[self.prescription_dose]
        #Find appropriate ROI
        if len(ROIs)==1:
            self.prescription_ROI = ROIs[0]
        else:
            #find the sortest one
            min_length = min([len(ROI) for ROI in ROIs])
            ROI = next(ROI for ROI in ROIs if len(ROI)== min_length)
        
            if 'opt'+ROI in ROIs:
                ROI = 'opt'+ROI
            
            self.prescription_ROI = ROI
            
        
        
        
        
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
        
        
    def check_for_couch(self):
         #make sure that couch is correct for treatment machine.
        ROI_names = [ROI.Name for ROI in self.case.PatientModel.RegionsOfInterest]
        if self.machine_name == 'ElektaVersaHD' :
            couch_structures = ['ElektaCouch']
            
        else: 
            couch_structures = ['Couch Top', 'Couch Inner', 'Couch Ribbon', 'Base Exterior', 'Base Interior']
            
            
        if sum([c in ROI_names for c in couch_structures]) != len(couch_structures):
            self.warnings.append('Couch top may be wrong or incomplete')
            
        
               
    def get_plan_name(self):
        plan_name = "CRS%d"%self.course_number
        plans = [plan.Name for plan in self.case.TreatmentPlans]
        if plan_name in plans:
            self.warnings.append('plan with same course number found, append site code to name to make course unique')
        while plan_name in plans:
            plan_name = plan_name + 'x'
            
        return plan_name
        
    def add_treatment_plan(self):
        
        with CompositeAction('Add Treatment plan'):
            plan_name = self.get_plan_name()
            self.plan = self.case.AddNewPlan(PlanName=plan_name, PlannedBy=r"Planner", Comment=r"", ExaminationName=self.exam.Name, IsMedicalOncologyPlan=False, AllowDuplicateNames=False)
        
            self.plan.SetDefaultDoseGrid(VoxelSize={ 'x': 0.2, 'y': 0.2, 'z': 0.2 })
            
            self.beam_set = self.plan.AddNewBeamSet(
                Name=r"CRS%dBS"%self.course_number, ExaminationName=self.exam.Name, 
                MachineName=self.machine_name, Modality="Photons", 
                TreatmentTechnique=self.treatment_technique, 
                PatientPosition="HeadFirstSupine", NumberOfFractions=self.num_fractions, 
                CreateSetupBeams=False, UseLocalizationPointAsSetupIsocenter=False,
                Comment=r"", RbeModelReference=None, EnableDynamicTrackingForVero=False,
                NewDoseSpecificationPointNames=[], NewDoseSpecificationPoints=[], 
                MotionSynchronizationTechniqueSettings={ 'DisplayName': None, 'MotionSynchronizationSettings': None, 'RespiratoryIntervalTime': None, 'RespiratoryPhaseGatingDutyCycleTimePercentage': None })

            self.beam_set.AddDosePrescriptionToRoi(RoiName=self.prescription_ROI, DoseVolume=95, PrescriptionType="DoseAtVolume", DoseValue=self.prescription_dose , RelativePrescriptionLevel=1, AutoScaleDose=False)
            
        self.patient.Save()
        self.plan.SetCurrent()
        
    def add_treatment_beams(self):
        # self.plan = get_current("Plan")
        # self.beam_set = get_current('BeamSet')
        iso = self.find_isocentre()
       
        if self.machine_name == 'ElektaVersaHD':
            retval_2 = self.beam_set.CreateArcBeam(ArcStopGantryAngle=181, ArcRotationDirection="CounterClockwise",
                                                   BeamQualityId=r"6", IsocenterData=iso, 
                                                   Name=r"%d.1"%self.course_number , Description=r"", GantryAngle=179, 
                                                   CouchRotationAngle=0, CouchPitchAngle=0, 
                                                   CouchRollAngle=0, CollimatorAngle=30)
            
            self.plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[0].ArcConversionPropertiesPerBeam.EditArcBasedBeamOptimizationSettings(CreateDualArcs=True, FinalGantrySpacing=4, MaxArcDeliveryTime=90, BurstGantrySpacing=None, MaxArcMU=None)

            retval_3 = self.beam_set.CreateArcBeam(ArcStopGantryAngle=185, ArcRotationDirection="CounterClockwise",
                                                   BeamQualityId=r"6", IsocenterData=iso, 
                                                   Name=r"%d.2"%self.course_number , Description=r"", GantryAngle=175, 
                                                   CouchRotationAngle=0, CouchPitchAngle=0, 
                                                   CouchRollAngle=0, CollimatorAngle=330)


        else:
            
      
            with CompositeAction('Add beam (1.1 Tomo, beam set: CRS1BS)'):#
            
              retval_0 = self.beam_set.CreatePhotonBeam(BeamQualityId=r"6", IsocenterData=iso,
                                                        Name=r"%d.1 Tomo"%self.course_number, Description=r"", GantryAngle=0,
                                                        CouchRotationAngle=0, CouchPitchAngle=0, CouchRollAngle=0, CollimatorAngle=0)

       
        
    def apply_clinical_goals(self):
        # plan = get_current('Plan')
        # template_name = 'ENT 7000/6300/5600'
        template_name = 'HeadAndNeckAutoPlanning'
        clinical_goals_template = self.db.LoadTemplateClinicalGoals(templateName =template_name, lockMode = 'Read')
        
        self.plan.TreatmentCourse.EvaluationSetup.ApplyClinicalGoalTemplate(Template=clinical_goals_template)
        clinical_goals_template.Unload()
        
        # plan.TreatmentCourse.EvaluationSetup.AddClinicalGoal(RoiName=r"PTV5240", GoalCriteria="AtLeast", GoalType="DoseAtVolume", AcceptanceLevel=5240, ParameterValue=0.95, IsComparativeGoal=False, Priority=1)

        
    def add_optimization_functions(self):
        # plan = get_current('Plan')
        if self.treatment_technique =='TomoHelical':
            plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[0].TomoPropertiesPerBeam.EditTomoBasedBeamOptimizationSettings(JawMode="Dynamic", PitchTomoHelical=0.43, PitchTomoDirect=None, BackJawPosition=1, FrontJawPosition=-1, MaxDeliveryTime=None, MaxGantryPeriod=None, MaxDeliveryTimeFactor=1.5)

        optimization_functions_template = self.db.LoadTemplateOptimizationFunctions(templateName ='ENT 7000/6300/5600 warm start EH', lockMode = 'Read' )
        self.plan.PlanOptimizations[0].ApplyOptimizationTemplate(Template=optimization_functions_template)
        
        optimization_functions_template.Unload()
        
    def find_isocentre(self):
        '''Finds the location of defined isocentre if it exists, if not creates
        it as the centre of the prescription ROI'''

        
        # self.beam_set = get_current('BeamSet') 
        iso = self.case.PatientModel.StructureSets[self.exam.Name].RoiGeometries[self.prescription_ROI].GetCenterOfRoi()
        print(iso)
        return self.beam_set.CreateDefaultIsocenterData(Position = iso)

    def run_optimization(self):
        optimization = self.plan.PlanOptimizations[0]
        optimization.OptimizationParameters.Algorithm.MaxNumberOfIterations = 40

        optimization.RunOptimization()
        optimization.OptimizationParameters.Algorithm.MaxNumberOfIterations = 40


warnings = ['The currently selected primary image set is assumed to be TPCT']
# def __init__(self, course_number = 3, machine_name = 'ElektaVersaHD', number_of_fx = 1):
def do_task(**options):
    print(options)
    add_treatment_plan(course_number = int(options['Course Number']),
                        machine_name = options['Treatment Machine'],
                        number_of_fx = int(options['Number Of Fractions'])).do_task()
    return

# def do_task(**options):
# 	print("\n\n\n**** QA BEGINNING\n\n\n")
#     # print(options)
# ## 	add_treatment_plan().do_task(careplan = options['selected_careplan'],  )
    
    
# 	print("\n\n\n**** PREPLAN QA FINISHED\n\n\n")
#  	print(options)
#     # {'selected_role': 'Planning', 'selected_site': 'Head and Neck', 'selected_careplan': 'H&N IMRT'}

if __name__ == '__main__':
    add_treatment_plan().do_task()
 