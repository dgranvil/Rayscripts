# -*- coding: utf-8 -*-
"""
Created on Tue Apr 13 11:24:11 2021
##Tested on cpython 3.6
@author: bywilson

Bug: add in check to see whether course exists and create unique name if it does
"""
from connect import *


class apply_clinical_goals :
    def __init__(self, care_plan):
        ##init things

        self.db = get_current("PatientDB")
        self.plan = get_current('Plan')
        self.careplan = care_plan
        

    def apply_clinical_goals(self):

        template_name = self.careplan +'_GOALS'
        clinical_goals_template = self.db.LoadTemplateClinicalGoals(templateName =template_name, lockMode = 'Read')
        
        self.plan.TreatmentCourse.EvaluationSetup.ApplyClinicalGoalTemplate(Template=clinical_goals_template)
        clinical_goals_template.Unload()
        
        # plan.TreatmentCourse.EvaluationSetup.AddClinicalGoal(RoiName=r"PTV5240", GoalCriteria="AtLeast", GoalType="DoseAtVolume", AcceptanceLevel=5240, ParameterValue=0.95, IsComparativeGoal=False, Priority=1)

def do_task(**options):
    
    print(options)
    apply_clinical_goals(care_plan = options[ 'selected_careplan']).apply_clinical_goals()
   
    return
        
