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
class create_DQA:
    def __init__(self):
        
        #initialization
        self.plan = get_current('Plan')
        self.case = get_current('Case')
        self.beamset = get_current('BeamSet')
        self.patient = get_current("Patient")
        self.tomo_machines =  ['T_TomoTherapy_1', 'T_TomoTherapy_2']
        self.isTomo =self.beamset.MachineReference.MachineName in self.tomo_machines

        self.warnings = []
        self.Testing = True 
        

    def create_DQA(self):
        ##Create DQA
        
        beamset = self.beamset


        if self.isTomo:
            #DQA phantom with tomo couch
            phantom_name = r"TomoD4v1 TomoD4v1"
            phantom_id =  r"TomoD4v1"
            
        else:
            #DQA phantom with elekta couch
            phantom_name = r"DELTA4OZ"
            phantom_id = r"DELTA4OZ"
        self.QA_plan_name =self.get_unique_QA_plan_name()
        
        
        #Tomo and ELekta have different couch models, so D4 have different models
        beamset.CreateQAPlan(PhantomName=phantom_name, PhantomId=phantom_id,
                              QAPlanName=self.QA_plan_name, 
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

        
        
    def send_dicom_file(self):
    
        #Send the plan to the appropriate place -> need to add justins server thing
        created_plan = next(P for P in self.plan.VerificationPlans if P.BeamSet.DicomPlanLabel == self.QA_plan_name)
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


    
def do_task(**options):
    DQA_module = create_DQA()
    DQA_module.create_DQA()
    
    set_progress_value(50)
    await_user_input('Please Verify that verification plan is good')
    DQA_module.send_dicom_file()
    
    


