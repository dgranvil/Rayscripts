# -*- coding: utf-8 -*-
"""
Created on Tue Apr 13 11:24:11 2021
##Tested on cpython 3.6
@author: bywilson

Bug: add in check to see whether course exists and create unique name if it does
"""
from connect import *


class add_optimization_functions :
    def __init__(self, careplan):
        ##init things
        
        self.patient = get_current('Patient')
        self.db = get_current("PatientDB")
        self.case = get_current('Case')
        self.plan = get_current('Plan')
        
        self.careplan = careplan
        ##find treatment technique from current plan
        
        
    def do_task(self):

        self.add_optimization_functions()
        self.run_optimization()
        
        
   
        
    def add_optimization_functions(self):
        
        # if self.treatment_technique =='TomoHelical':
        #     self.plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[0].TomoPropertiesPerBeam.EditTomoBasedBeamOptimizationSettings(JawMode="Dynamic", PitchTomoHelical=0.43, PitchTomoDirect=None, BackJawPosition=1, FrontJawPosition=-1, MaxDeliveryTime=None, MaxGantryPeriod=None, MaxDeliveryTimeFactor=1.5)

        optimization_functions_template = self.db.LoadTemplateOptimizationFunctions(templateName =self.careplan, lockMode = 'Read' )
        self.plan.PlanOptimizations[0].ApplyOptimizationTemplate(Template=optimization_functions_template)
        
        optimization_functions_template.Unload()
        
  

    def run_optimization(self):
        optimization = self.plan.PlanOptimizations[0]
        optimization.OptimizationParameters.Algorithm.MaxNumberOfIterations = 40

        optimization.RunOptimization()
        optimization.OptimizationParameters.Algorithm.MaxNumberOfIterations = 40
        
        
def do_task(**options):
    print(options)
    
    add_optimization_functions(careplan = options['selected_careplan']).do_task()
    
    return


        
        # isocentre_POI = [POI for POI in  self.case.PatientModel.PointsOfInterest if POI.Type == 'Isocenter']
        # if len(isocentre_POI)>1:
        #     POI = isocentre_POI[0]
        #     self.warnings.append('two isocentres defined, selected one arbitrarily')
            
        # elif len(isocentre_POI):
        #     POI = isocentre_POI[0]
            
            
        # else:
        #     self.warnings.append('centre of precsription target used for isocentre')

