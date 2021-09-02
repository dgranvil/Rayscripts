"""
Assumes that the current scan is the TPCT
Bug: If run multiple times, couch in wrong vertical pos'n
"""

from connect import *
import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")
from System.Windows.Forms import Application, Form, Label, ComboBox, Button
from System.Drawing import Point, Size


class add_treatment_couch:
    
    def __init__(self):
        self.case = get_current('Case')
        examination = get_current("Examination")
        db = get_current("PatientDB")
        self.plan = get_current('Plan')
        ##Find couch type from plan
        
        couch_type = self.find_couch_type_to_add()
       
        ##Look whether it already exists
            
        couch_type = self.check_for_couch(couch_type)   
        
        
        if couch_type in ['Elekta', 'Tomo']:

            TableHeight = float(examination.GetStoredDicomTagValueForVerification(Group = 0x0018, Element = 0x1130)['TableHeight'])/10.
            

            if couch_type == 'Tomo':
                ##add tomo couch
                couchROINames = [r"Couch Top", r"Couch Inner", r"Couch Ribbon", r"Base Exterior", r"Base Interior"]
                self.case.PatientModel.CreateStructuresFromTemplate(SourceTemplate=db.LoadTemplatePatientModel(templateName ='Tomo HDA Couch Extended', lockMode = 'Read'), 
                                                                SourceExaminationName=r"TPCT1Jan21OMR", 
                                                                SourceRoiNames=couchROINames, 
                                                                SourcePoiNames=[], AssociateStructuresByName=True, 
                                                                TargetExamination=examination, InitializationOption="AlignImageCenters")
            
                CouchModelDistanceToCentre = -10.85 -(-26.1) +0.34
                contour_dy =  TableHeight  - CouchModelDistanceToCentre
                contour_dx = 0

            elif couch_type == 'Elekta':
                ##add elekta couch
                couchROINames = [r"ElektaCouch"]
                self.case.PatientModel.CreateStructuresFromTemplate(SourceTemplate=db.LoadTemplatePatientModel(templateName = 'Elekta Couch Top', lockMode = 'Read'), 
                                                                SourceExaminationName=r"CT 1", SourceRoiNames=couchROINames,
                                                                SourcePoiNames=[], AssociateStructuresByName=True, 
                                                                TargetExamination=examination, InitializationOption="AlignImageCenters")
                CouchModelDistanceToCentre = -10.85 -(-21.86)
                contour_dy =  TableHeight  - CouchModelDistanceToCentre
                contour_dx = -1.7
                
                
            TForm =  {'M11':1, 'M12':0, 'M13':0, 'M14':contour_dx,
                      'M21':0, 'M22':1, 'M23':0, 'M24':contour_dy,
                      'M31':0, 'M32':0, 'M33':1, 'M34':0,
                      'M41':0, 'M42':0, 'M43':0, 'M44':1}
            
            for ROI in couchROINames:
                
                self.case.PatientModel.RegionsOfInterest[ROI].TransformROI3D(Examination = examination,
                                                                        TransformationMatrix = TForm)
            # Extend couch model
            if couch_type == 'Elekta':
                for ROI in couchROINames:
                
                    #Extend couch geometries to encapsulate the entire CT1
                    self.case.PatientModel.RegionsOfInterest[ROI].CreateMarginGeometry(Examination=examination, SourceRoiName=ROI, MarginSettings={ 'Type': "Expand", 'Superior': 15, 'Inferior': 15, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

            #Set default dose grid size if not already done so
            #Maybe these should be the one that are already selected.
            current_voxel_size = self.plan.TreatmentCourse.TotalDose.InDoseGrid.VoxelSize
            self.plan.SetDefaultDoseGrid(VoxelSize=current_voxel_size)
            self.plan.TreatmentCourse.TotalDose.UpdateDoseGridStructures()

        elif couch_type == 'None':
            show_warning('Error: no couch added, please add manually', level = 'warn')

    def find_couch_type_to_add(self):

        machine_name = self.plan.BeamSets[0].MachineReference.MachineName
        if machine_name in ['ElektaVersaHD']:
            couch_type = 'Elekta'
        elif machine_name in ['T_TomoTherapy_1', 'T_TomoTherapy_2']:
            couch_type = 'Tomo'
        else:
            
            couch_type = 'None'
        return couch_type
    
    def check_for_couch(self, couch_type):
        #make sure that couch is correct for treatment machine.
        couch_structures = ['Couch Top', 'Couch Inner', 'Couch Ribbon',
                            'Base Exterior', 'Base Interior', 'ElektaCouch']
        ROI_names = [ROI.Name for ROI in self.case.PatientModel.RegionsOfInterest]

        if sum([c in ROI_names for c in couch_structures]) >0:
            
            show_warning('Error: Couch structure may already be added, please delete or add manually')
            couch_type = "None"
        return couch_type
    
    
# warnings = ['Please Select Treatment Unit']
def do_task(**options):
    print("\n\n\n**** COUCH PLACEMENT BEGINNING\n\n\n")
    add_treatment_couch()
    print("\n\n\n**** COUCH PLACEMENT FINISHED\n\n\n")











