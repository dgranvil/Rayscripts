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
class create_isodose_contours:
    def __init__(self):
        
        self.plan = get_current('Plan')
        self.case = get_current('Case')
        self.beamset = get_current('BeamSet')
        self.patient = get_current("Patient")
         

        ROIs = self.case.PatientModel.RegionsOfInterest
        prescription_doses = set()
        for ROI in ROIs:
            if ROI.Type == 'Ptv' or 'ptv' in ROI.Name.lower():
                N = self.find_dose_from_PTV_name(ROI.Name)
                if N != None:
                    prescription_doses.add(N)


        dose_distribution = self.beamset.FractionDose
        Colours = ['Orange','Red','Blue','White', 'Green'] #maybe shouldnt be random colours
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
    create_isodose_contours()

