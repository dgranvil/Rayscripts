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

class sum_all_dose:
    
    def __init__(self):

        case = get_current("Case")
        # self.beam_set = get_current("BeamSet")
        examination = get_current("Examination")

        
        ##sum the doses
                #Find the appropriate dose distribution for each of the plans
                #either the initial one or the one of the transferred dose
        dose_distributions = []
        dose_weights = []
        sum_name = 'sum'
        
        fraction_evaluation =case.TreatmentDelivery.FractionEvaluations[0] #Dont know if there are cases where there would be multiple 
        transferred_dose_evaluations= [dose for dose in fraction_evaluation.DoseOnExaminations[0].DoseEvaluations
                                       if 'OfDoseDistribution' in dir(dose)]
        # ##make a dictionary that relates plan name to fraction evaluations     
        for plan in case.TreatmentPlans: 
            plan_scan_name = plan.TreatmentCourse.TreatmentFractions[0].BeamSet.PatientSetup.LocalizationPoiGeometrySource.OnExamination.Name
            if plan_scan_name != examination.Name: #plan is a transferred dose
                ##look through the fraction evaluations for the dose that comes from the dicom UID
                dose_UID = plan.BeamSets[0].FractionDose.ModificationInfo.DicomUID
                
                
                
                dose_eval_list = [dose_eval for dose_eval in transferred_dose_evaluations 
                                  if dose_eval.OfDoseDistribution.ModificationInfo.DicomUID == dose_UID]
                if len(dose_eval_list)>1:
                    warning('More then one dose mapping for plan ' + plan.Name)
                elif len(dose_eval_list)==0:
                    warning('Could not find a dose mapping for plan ' + plan.Name)
                else:
                    dose_distributions.append(dose_eval_list[0])
                    dose_weights.append(plan.BeamSets[0].FractionationPattern.NumberOfFractions)
                    sum_name += plan.Name 
              
            else:
                #plan dose is already on TPCT

                dose_distributions.append(plan.BeamSets[0].FractionDose) 
                dose_weights.append(plan.BeamSets[0].FractionationPattern.NumberOfFractions)
                sum_name += plan.Name 

        
        if len(dose_distributions)>1:
            retval_0 = case.CreateSummedDose(DoseName=sum_name, FractionNumber=0,
                                              DoseDistributions=dose_distributions, 
                                              Weights=dose_weights)
        else:
            warning('could not find two plans to sum, sum not created')

def do_task(**options):
    sum_all_dose()
    
if __name__ == '__main__':
    def warning(text_message):
        print(text_message)
    sum_all_dose()

