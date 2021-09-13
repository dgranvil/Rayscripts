# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 17:31:10 2021

@author: bywilson
"""

# from connect import *

# class create_dose_composite():
#     def create_hybrid_registration():
        
from connect import *
from collections import defaultdict

class transfer_dose_to_primary_scan:
    
    def __init__(self):

        self.case = get_current("Case")
        # self.beam_set = get_current("BeamSet")
        self.examination = get_current("Examination")

        
        frame_of_reference = dict()
        
        for exam in self.case.Examinations:
            frame_of_reference[exam.Name] = exam.EquipmentInfo.FrameOfReference
        
        registration_to_use = dict()
        for registration in self.case.Registrations:
            FoR = registration.FromFrameOfReference
            print(FoR,registration.FromFrameOfReference,  self.examination.EquipmentInfo.FrameOfReference)
            if registration.ToFrameOfReference != self.examination.EquipmentInfo.FrameOfReference:
                continue
            
            if FoR in registration_to_use.keys():
                warning('multiple registrations for same image pair, please do dose sum manually')
                return
            
            registration_to_use[FoR] = registration
  
        
        ##map the doses     
        for plan in self.case.TreatmentPlans:
            plan_scan_name = plan.TreatmentCourse.TreatmentFractions[0].BeamSet.PatientSetup.LocalizationPoiGeometrySource.OnExamination.Name
            if plan_scan_name != self.examination.Name:
                
                #find the registration to use
                plan_frame_of_reference = frame_of_reference[plan_scan_name]
                print(plan_frame_of_reference, registration_to_use)
                ##scan is not the TPCT, deform dose
                registration = registration_to_use[plan_frame_of_reference]
                ##look for the correct registration set
                
                # if len(registration.StructureRegistrations)>1:
                #     warning('multiple structure registrations, please do dose registration manually')
                
                #BUG, check to see whether the dose has been mapped previously
                result = self.case.MapDose(FractionNumber=0, SetTotalDoseEstimateReference=True, 
                              DoseDistribution=plan.BeamSets[0].FractionDose, 
                              StructureRegistration=registration.StructureRegistrations[1])


def do_task(**options):
    transfer_dose_to_primary_scan()


def warning(text_message):
    print(text_message)
  

if __name__ == '__main__':
    transfer_dose_to_primary_scan()

