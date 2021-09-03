from connect import *


class load_structure_template:
    
    def __init__(self):
        self.case = get_current("Case")
        self.examination = get_current("Examination")
        self.db = get_current("PatientDB")
        
        # Dict with keys = name of structure template in RayStation
        #           values = list of applicable careplans as defined in rayscripts confid
        self.template_matching_OARs = {'H&N OARs' : ['H&N IMRT']
        }

    def load_template(self, selected_careplan): 
        # Decide which template to use  
        for template in self.template_matching_OARs.keys():
            if selected_careplan in self.template_matching_OARs[template]:
                T = self.db.LoadTemplatePatientModel(templateName = template)
                source_ROI_names = T.PatientModel.RegionsOfInterest.Keys
                source_POI_names = T.PatientModel.PointsOfInterest.Keys
                self.case.PatientModel.CreateStructuresFromTemplate(
                    SourceTemplate = T,
                    SourceExaminationName=T.StructureSetExaminations[0].Name,
                    SourceRoiNames=source_ROI_names, 
                    SourcePoiNames=source_POI_names,
                    AssociateStructuresByName=True, TargetExamination=self.examination, InitializationOption="EmptyGeometries")
                T.Unload()

                break


def do_task(**options):
    load_structure_template().load_template(selected_careplan = options['selected_careplan'])

