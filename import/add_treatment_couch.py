"""
Assumes that the current scan is the TPCT
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
        self.examination = get_current("Examination")
        self.db = get_current("PatientDB")

    def do_task(self, couch_type):

        if couch_type in ['Elekta', 'Tomo']:
            case = self.case
            examination = self.examination
            db = self.db
                
            TableHeight = float(examination.GetStoredDicomTagValueForVerification(Group = 0x0018, Element = 0x1130)['TableHeight'])/10

            if couch_type == 'Tomo':
                
                ## check if couch already exists - if so, delete and display warning
                ## if we don't delete first, it'll transform the existing couch and shift from correct location
                couchROINames = [r"Couch Top", r"Couch Inner", r"Couch Ribbon", r"Base Exterior", r"Base Interior"]
                self.delete_existing_couch(couchROINames)

                ##add tomo couch
                case.PatientModel.CreateStructuresFromTemplate(SourceTemplate=db.LoadTemplatePatientModel(templateName ='Tomo HDA Couch Extended', lockMode = 'Read'), 
                                                                SourceExaminationName=r"TPCT1Jan21OMR", 
                                                                SourceRoiNames=couchROINames, 
                                                                SourcePoiNames=[], AssociateStructuresByName=True, 
                                                                TargetExamination=examination, InitializationOption="AlignImageCenters")
            
                CouchModelDistanceToCentre = -10.85 -(-26.1) +0.34
                contour_dy =  TableHeight  - CouchModelDistanceToCentre
                contour_dx = 0

            elif couch_type == 'Elekta':

                ## check if couch already exists - if so, delete and display warning
                ## if we don't delete first, it'll transform the existing couch and shift from correct location
                couchROINames = [r"ElektaCouch"]
                self.delete_existing_couch(couchROINames)

                ##add elekta couch
                case.PatientModel.CreateStructuresFromTemplate(SourceTemplate=db.LoadTemplatePatientModel(templateName = 'Elekta Couch Top', lockMode = 'Read'), 
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
                
                case.PatientModel.RegionsOfInterest[ROI].TransformROI3D(Examination = examination,
                                                                        TransformationMatrix = TForm)
            # Extend couch model
            if couch_type == 'Elekta':
                for ROI in couchROINames:
                
                    #Extend couch geometries to encapsulate the entire CT1
                    case.PatientModel.RegionsOfInterest[ROI].CreateMarginGeometry(Examination=examination, SourceRoiName=ROI, MarginSettings={ 'Type': "Expand", 'Superior': 15, 'Inferior': 15, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

            return 1

        elif couch_type == 'None':
            show_warning('No Couch Type selected.\nCouch structure not drawn.')

    def delete_existing_couch(self, couchROINames):
    	for couchROIName in couchROINames:
    		if couchROIName in [x.Name for x in self.case.PatientModel.RegionsOfInterest]:
    			self.case.PatientModel.RegionsOfInterest[couchROIName].DeleteRoi()
    			print('deleting ', couchROIName)
    			show_warning('Couch already existed.\nPrevious couch deleted and replaced.')
    	return 1

    def do_QC(self):
        return -1



def do_task(**options):
    print("\n\n\n**** COUCH PLACEMENT BEGINNING\n\n\n")
    add_treatment_couch().do_task(couch_type = options['Couch Type'])
    print("\n\n\n**** COUCH PLACEMENT FINISHED\n\n\n")










