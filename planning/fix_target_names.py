# -*- coding: utf-8 -*-
"""
Created on Mon Jul 26 13:39:21 2021
Add crs number to each of the target structures
should I force a naming convention? I dont think, because the naming will be
in the templates.

@author: bywilson
"""

from connect import get_current
import re

class fix_structure_names:
    def __init__(self):
        self.case = get_current('Case')
        self.examination = get_current('Examination')
        self.plan = get_current('Plan')
        #Find course number
        self.course_number = self.get_course_number()
        
        target_structures = [ROI for ROI in self.case.PatientModel.RegionsOfInterest if
                             ROI.Type in ['Ptv', 'Ctv','Gtv'] ]
        _ = [self.add_course_number_to_name(ROI) for ROI in target_structures]
        
  
        
    def get_course_number(self):
        #find the course number from the treatment course name
            #using complex re expression that finds ints and decimal like numbers
        crs_number_candidates = re.findall(r"[-+]?\d*\.\d+|\d+", self.plan.Name) 

        if len(crs_number_candidates) == 1:
            crs_number = crs_number_candidates[0]
            
        else:
            warning('Could not find course number, please rename plan name to contain only 1 number')
            return ''
        return crs_number #crs_number is a string
    
    
    def add_course_number_to_name(self,ROI):
        
        
        ROINameSplit = re.split('(\d+)', ROI.Name) #splits the ROI by int/not int
        if not ROINameSplit[0].isnumeric():
            ##Make the change to the ROI
            ROI.Name = self.course_number + ROI.Name
            print(self.course_number, ROINameSplit)
        
        

def do_task(**options):
    print(options)
    fix_structure_names()
    
   
    return
if __name__ == '__main__':
    fix_structure_names()




