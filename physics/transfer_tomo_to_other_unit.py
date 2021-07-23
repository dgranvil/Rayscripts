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
class create_transferred_tomo_plan:
    def __init__(self):
        
        self.plan = get_current('Plan')
        self.case = get_current('Case')
        self.beamset = get_current('BeamSet')
        self.patient = get_current("Patient")

        self.tomo_machines =  ['T_TomoTherapy_1', 'T_TomoTherapy_2']
        self.isTomo =self.beamset.MachineReference.MachineName in self.tomo_machines
        self.TPCT = self.beamset.PatientSetup.OfTreatmentSetup.PatientSetup.LocalizationPoiGeometrySource.OnExamination.Name
        self.warnings = []
        self.Testing = True 
        
 
    
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
 
 

def do_task(**options):
    create_transferred_tomo_plan()

    


