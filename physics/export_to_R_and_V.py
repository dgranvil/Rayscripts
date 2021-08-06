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
class export_to_R_and_V:
    def __init__(self):
        
        self.plan = get_current('Plan')
        self.case = get_current('Case')
        self.beamset = get_current('BeamSet')

        self.isApproved = self.plan.Review.ApprovalStatus == 'Approved'
        #check whether the plan is approved
        
        if self.plan.Review == None:
            self.warnings.append('The plan is not reviewed')
            self.isApproved = False
        else:
            self.isApproved = self.plan.Review.ApprovalStatus == 'Approved'
            
 
        self.tomo_machines =  ['T_TomoTherapy_1', 'T_TomoTherapy_2']
        self.isTomo =self.beamset.MachineReference.MachineName in self.tomo_machines
        self.TPCT = self.beamset.PatientSetup.OfTreatmentSetup.PatientSetup.LocalizationPoiGeometrySource.OnExamination.Name
        self.warnings = []

        
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
            
    

def do_task(**options):
    export_to_R_and_V()
    

