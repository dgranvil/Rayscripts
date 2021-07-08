from connect import *

class segment_structures:
    on_by_default = 0
    def __init__(self):
        self.case = get_current("Case")
        self.examination = get_current("Examination")
        self.db = get_current("PatientDB")
        self.warnings = []
    
    def do_task(self, site):  
        if site == 'Head and Neck':
            self.db.RunOarSegmentation(ModelName='HN', Examinations = [self.examination.Name], Registrations = [None])
        elif site == 'Breast':
            self.db.RunOarSegmentation(ModelName='Thorax', Examinations = [self.examination.Name], Registrations = [None])
        else:
            show_warning('No DL segmenation for selected site')

def do_task(**options):
    print("\n\n\n**** DEEP LEARNING SEGMENTATION BEGINNING\n\n\n")
    segment_structures().do_task(site = options['selected_site'])
    print("\n\n\n**** DEEP LEARNING SEGMENTATION FINISHED\n\n\n")











