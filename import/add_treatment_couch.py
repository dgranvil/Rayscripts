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

    def do_task(self, couch_type = 0):
        if couch_type == 0:
            form = select_couch_form()
            Application.Run(form)
            couch_type = form.couch_type
        
        case = self.case
        examination = self.examination
        db = self.db
            
        TableHeight = float(examination.GetStoredDicomTagValueForVerification(Group = 0x0018, Element = 0x1130)['TableHeight'])/10
        
        
        

        if couch_type == 'Tomo':
            ##add tomo couch
            couchROINames = [r"Couch Top", r"Couch Inner", r"Couch Ribbon", r"Base Exterior", r"Base Interior"]
            case.PatientModel.CreateStructuresFromTemplate(SourceTemplate=db.LoadTemplatePatientModel(templateName ='Tomo HDA Couch Extended', lockMode = 'Read'), 
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

    def do_QC(self):
        return -1


class select_couch_form(Form):
    
    def __init__(self):
        # Set the size of the form
        self.Size = Size(300, 200)
        # Set title of the form
        self.Text = 'Select Couch Type'
        # Add a label
        label = Label()
        label.Text = 'Please select the treatment couch type'
        label.Location = Point(15, 15)
        label.AutoSize = True
        self.Controls.Add(label)

        # Add a ComboBox that will display the ROI:s to select
        # Define the items to show up in the combobox,
        # we only want to show ROI:s with geometries
        # defined in the structure set of the current plan
        couch_types = ['Tomo', 'Elekta', 'Elekta + Carbon Fibre Head Holder']
        self.combobox = ComboBox()
        self.combobox.DataSource = couch_types
        self.combobox.Location = Point(15, 60)
        self.combobox.AutoSize = True
        self.Controls.Add(self.combobox)
        # Add button to press OK and close the form
        button = Button()
        button.Text = 'OK'
        button.AutoSize = True
        button.Location = Point(15, 100)
        button.Click += self.ok_button_clicked
        self.Controls.Add(button)

    def ok_button_clicked(self, sender, event):
        # Method invoked when the button is clicked
        # Save the selected ROI name
        self.couch_type = self.combobox.SelectedValue
        # Close the form
        self.Close()

def do_task():
	print("\n\n\n**** COUCH PLACEMENT BEGINNING\n\n\n")
	add_treatment_couch().do_task()
	print("\n\n\n**** COUCH PLACEMENT FINISHED\n\n\n")










