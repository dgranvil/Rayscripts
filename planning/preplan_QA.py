# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 13:18:29 2021
QA Script to be ran before planning
Assumes that the current primary case is the TPCT
@author: bywilson
"""


from connect import *
import numpy as np
#from physics_QA import physics_QA

class preplan_QA:
    
    
    def __init__(self):
        self.warnings = []
        self.case = get_current('Case')
        self.examination = self.find_TPCT()
       
        # self.examination = get_current('Examination')
        #maybe set TPCT to current?
        
        
    def do_task(self):
        
        self.fix_deep_learning_segmentation_error()
        self.update_derived_contours()
        self.find_empty_structures()
        self.find_underived_PTVs()
        self.check_for_high_density()
        self.check_for_overlap()
        
        # physics_QA_i = physics_QA()
        # physics_QA_i.check_couch()
        # self.warnings += physics_QA_i
        
        
        self.print_warnings()
        
  
    def print_warnings(self):
        for m in self.warnings:
            print(m)
            
    def find_TPCT(self, CTSimulators = ['HOST-76205','HOST-7055','PHILIPS-7055'] ):
        '''Looks for the most recent examination that contains the structures
        if the TPCT is greater than 21 days old, will append a warning '''
        #make sure that the TPCT is recent and appropreate
        ##Look for the most recent examination
        # help_message = 'Could not find the TPCT, please select it as the primary scan '
        
        TPCT_candidates = [exam for exam in self.case.Examinations 
                           if exam.GetAcquisitionDataFromDicom()['EquipmentModule']['StationName'] 
                           in CTSimulators]
        
        exam_dates = [exam.GetExaminationDateTime() for exam in TPCT_candidates]
        if len(exam_dates) == 0:
            TPCT_candidates = []
        else:
            most_recent_date = max(exam_dates).Date
            
            if most_recent_date.Today.Subtract(most_recent_date).Days>21:
                self.warnings.append('The most recent TPCT is greater than 21 days old')
            
            TPCT_candidates = [TPCT_candidates[i] for i, d in enumerate(exam_dates)
                               if d.Date == most_recent_date]
        
        
        ##if still than more candidate, look for one with most targets defined
        if len(TPCT_candidates) == 1:
            return TPCT_candidates[0]
        elif len(TPCT_candidates)>1:
            ####find the one with contoured PTVs
            PTVs = [ROI for ROI in self.case.PatientModel.RegionsOfInterest if ROI.Type =='Ptv']
            num_PTV_contours = np.zeros(len(TPCT_candidates))
            
            for i, PTV in enumerate(PTVs):
                for j, TPCT in enumerate(TPCT_candidates):
                    PTV_structure_set = self.case.PatientModel.StructureSets[TPCT.Name].RoiGeometries[PTV.Name]
                    if PTV_structure_set.HasContours():
                        num_PTV_contours[j] +=1
            TPCT = TPCT_candidates[ num_PTV_contours.argmax()]
            
            
            
        else:
            await_user_input('Could not find the TPCT, please select it as the primary scan ')
            return get_current('Examination')
            
        
    
        return TPCT
    
    
        
        
    def find_empty_structures(self, print_statement = 0):
        '''Assuming that the current examination is the TPCT, this function goes 
        through each of the ROIs and returns a list of ROI names which do not have 
        any contours in them'''
        

        ROI_geometries = self.case.PatientModel.StructureSets[self.examination.Name].RoiGeometries
        NoContours = []
        for ROI in ROI_geometries:
            if not(ROI.HasContours()):
                NoContours.append(ROI.OfRoi.Name)
        if print_statement:
            print('The Empty Structures are', NoContours)
    
        if len(NoContours):
            self.warnings.append('The empty structures are :' + ', '.join(NoContours))
        
        


    def find_underived_PTVs(self,  print_statement = 0):
        '''Find all PTVs that are underiver and append them to self.warnings'''

        ROIs = self.case.PatientModel.RegionsOfInterest
        not_derived = []
        for ROI in ROIs:
            if ROI.Type == 'Ptv':
                if ROI.DerivedRoiExpression == None:
                    not_derived.append(ROI.Name)
        if print_statement:
            print('PTVs that arent derived', not_derived)
        if len(not_derived):
            self.warnings.append( 'PTVs that arent derived' + str( not_derived))
        
        else:
            return None
        
    def fix_deep_learning_segmentation_error(self):
        '''Goes through each structure and 
        field safety notice states that deep learning contours need to be converted
        to contours or structure expansions are innacurate. Bug will be fixed
        in next version of raystation (11)'''
        
        #for structure in TPCT structure set
        for ROI in self.case.PatientModel.StructureSets[self.examination.Name].RoiGeometries:
            if ROI.HasContours():
                ROI.SetRepresentation(Representation = 'Contours')
    
    def update_derived_contours(self):
        ##Go through each of the structures and update the derived contours if they exist
        derived_ROI = [ROI for ROI in self.case.PatientModel.RegionsOfInterest if ROI.DerivedRoiExpression != None]
        
        for ROI in derived_ROI:
            
            ROI.UpdateDerivedGeometry(Examination = self.examination)
                
    def check_for_high_density(self):
        try:
            high_density_statistics = self.examination.Series[0].ImageStack.GetIntensityStatistics(RoiName = 'external')
            if high_density_statistics['Max'] > 2000:
                self.warnings.append('Image has region of >2000 HU, please check that high density material has been properly accounted for')
                ##Maybe print out the location with teh get max grey level location function
                
        except:
            self.warnings.append('high density check failed, please ensure that high density material is properly accounted for')
        return
    
    def check_for_overlap(self):
        '''Checks for overlap for '''
        ROI_names = [ROI.Name for ROI in self.case.PatientModel.RegionsOfInterest]
        pairs_that_shouldnt_overlap=[['SpinalCord','Brainstem'], ['OpticNerve_L','Chiasm'],['OpticNerve_R','Chiasm']]
        pairs_that_should_overlap=[['PRV_OpticNerve_R', 'Chiasm'],['PRV_OpticNerve_L','Chiasm'],['PRV_SpinalCord', 'Brainstem'] ]
        for pair in pairs_that_shouldnt_overlap:
            if sum([OAR in ROI_names for OAR in pair]) == 2:
                structure_sets = self.case.PatientModel.StructureSets[self.examination.Name]
                
                Comparison = structure_sets.ComparisonOfRoiGeometries(
                                RoiA = pair[0], RoiB = pair[1], 
                                ComputeDistanceToAgreementMeasures= False)
                print(pair, Comparison)
                if Comparison['DiceSimilarityCoefficient']>0:
                    self.warnings.append('overlap detected between structures: %s and %s' % (pair[0] , pair[1]))
                
        for pair in pairs_that_should_overlap:
            if sum([OAR in ROI_names for OAR in pair]) == 2:
                structure_sets = self.case.PatientModel.StructureSets[self.examination.Name]
                
                Comparison = structure_sets.ComparisonOfRoiGeometries(
                                RoiA = pair[0], RoiB = pair[1], 
                                ComputeDistanceToAgreementMeasures= False)
        
                if Comparison['DiceSimilarityCoefficient']==0:
                    print(pair, Comparison)
                    self.warnings.append('structures are farther than PRV margin: %s and %s' % (pair[0] , pair[1]))

        # print(self.warnings)
#Figure out whether there is overlap/abutting of structures that need to do so

warnings = ['test1']
def do_task(**options):
	print("\n\n\n**** PREPLAN QA BEGINNING\n\n\n")
	preplan_QA().do_task()
    
	print("\n\n\n**** PREPLAN QA FINISHED\n\n\n")
	print(options)


# if __name__ =="__main__":
#     A = preplan_QA()
#     A.find_empty_structures()
#     A.print_warnings()
#Navigate user to fusions?

    
#Look for imhomogeneities and flag the user to for possibe overrides

#lookf or high density artifacts around mandible/lips
        
# case.PatientModel.UpdateDerivedGeometries()

