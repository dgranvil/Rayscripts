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
        self.warnings = []
        self.plan = get_current('Plan')
        self.case = get_current('Case')
        self.beamset = get_current('BeamSet')
        self.patient = get_current("Patient")
        self.Testing = True 
        
        
        
        self.tomo_machines =  ['T_TomoTherapy_1', 'T_TomoTherapy_2']
        self.isTomo =self.beamset.MachineReference.MachineName in self.tomo_machines
        self.TPCT = self.beamset.PatientSetup.OfTreatmentSetup.PatientSetup.LocalizationPoiGeometrySource.OnExamination.Name
        
        #check whether the plan is approved
        
        if self.plan.Review == None:
            self.warnings.append('The plan is not reviewed')
            self.isApproved = False
        else:
            self.isApproved = self.plan.Review.ApprovalStatus == 'Approved'
            
 
 
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
        if not self.Testing:
        
            if self.beamset.ModificationInfo.SoftwareVersion != '10.0.1.52':
                self.warnings.append('Wrong Raystation software version')
        
        #Check whether energy is correct for VMAT
        if not self.isTomo:
            for beam in self.beamset.Beams:
                if beam.DeliveryTechnique == 'DynamicArc' and beam.BeamQualityId != '6':
                    self.warnings.append('VMAT beam %s not a comissioned energy' %beam.Name )
        
        #make sure that voxel spacing is approriate 2mm or less
        for direction in 'xyz':
            if self.beamset.FractionDose.InDoseGrid.VoxelSize[direction]>0.2:
                self.warnings.append('dose voxel size greater than 2mm')
        
        
        #Make sure that the correctcouch is applied for the treatment unit
        self.check_couch()
        
        self.print_warnings()
        
    def print_warnings(self):
        for m in self.warnings:
            print(m)
                  
    
    def check_couch(self):
         #make sure that couch is correct for treatment machine.
        ROI_names = [ROI.Name for ROI in self.case.PatientModel.RegionsOfInterest]
        if self.isTomo:
            couch_structures = ['Couch Top', 'Couch Inner', 'Couch Ribbon', 'Base Exterior', 'Base Interior']
        else: 
            couch_structures = ['ElektaCouch']
            
        if sum([c in ROI_names for c in couch_structures]) != len(couch_structures):
            self.warnings.append('Couch top may be wrong or incomplete')


def do_task(**options):
    physics_QA()
 
