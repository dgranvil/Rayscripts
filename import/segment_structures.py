#Does not currently work well due to bug in RayStation itself
#DL autosegmentation is slow and crashes frequently when run by scripting
#It works well when run using GUI, though

from connect import *

class structure_segmentation:
    on_by_default = 0
    def __init__(self):
        self.case = get_current("Case")
        self.examination = get_current("Examination")
        self.db = get_current("PatientDB")
        self.warnings = []
    
    def segment_structures(self, site):  
        if site == 'Head and Neck':
            self.db.RunOarSegmentation(ModelName='HN', Examinations = [self.examination.Name], Registrations = [None])
        elif site == 'Breast':
            self.db.RunOarSegmentation(ModelName='Thorax', Examinations = [self.examination.Name], Registrations = [None])
        else:
            show_warning('No DL segmenation for selected site')

def do_task(**options):
    structure_segmentation().segment_structures(site = options['selected_site'])












