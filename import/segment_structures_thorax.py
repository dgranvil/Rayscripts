from connect import *

class segment_structures:
    on_by_default = 0
    def __init__(self):
        self.case = get_current("Case")
        self.examination = get_current("Examination")
        self.db = get_current("PatientDB")
        self.warnings = []
    
    def do_task(self):     
        self.db.RunOarSegmentation(ModelName='Thorax', Examinations = [self.examination.Name], Registrations = [None])

def do_task():
	print("\n\n\n**** DEEP LEARNING SEGMENTATION BEGINNING\n\n\n")
	segment_structures().do_task()
	print("\n\n\n**** DEEP LEARNING SEGMENTATION FINISHED\n\n\n")












