
"""
Bugs:
    ->need to make it not do anything if the stuff is already in a group
        try statements?
        
    ->need to make it not fail when it has two unique names

n assuming we're correct and forcing rename, display window that shows name mappings. Have user verify correct or edit as needed.
    
"""



from connect import *
from collections import defaultdict

class rename_simulation_scans:


	### Variables that should go in config
    MRNamePairs ={'SAG T1 SPACE':'ST1',  'AX T2 BLADE SPAIR (3mm)':'T2B' , 'AX VIBE DIXON':'VBC' }
    CTSimulators = ['HOST-76205','HOST-7055','PHILIPS-7055']
    on_by_default = 1
    
    def __init__(self):
        
        self.warnings = []
        self.case = get_current("Case")
        self.patient = get_current('Patient')
        
        
    def rename_scans(self):

        case = self.case      
        
        TPCT = self.find_TPCT()
        if TPCT != -1:
            TPCT.SetPrimary()
            
        
        MRGroup = defaultdict(list)
        
        PETGroup = defaultdict(list)
        
        
        #Rename each of the study set to the correct name
        
        for exam_number , examination in enumerate(self.case.Examinations):
            dcmdata = examination.GetAcquisitionDataFromDicom()
            StationName = dcmdata['EquipmentModule']['StationName']
            print(StationName, exam_number)
            ending = str(exam_number)
            if StationName in self.CTSimulators:
                scanType = 'TPCT'
                ending = ''
                
                if self.detect_tags(dcmdata,tags = ['Venous']):
                    ending += '_VEN'
                elif self.detect_tags(dcmdata,tags = ['Arterial']):
                    ending += '_ART'
                if self.detect_tags(dcmdata,tags = ['O-MAR','OMR','OMAR']):
                    ending+= '_OMR'
                    
        
        
            elif examination.EquipmentInfo.Modality=='MR':
                                
                scanType = 'TPMR'
                
                
                if dcmdata['SeriesModule']['SeriesDescription'] in self.MRNamePairs:
                    ending = self.MRNamePairs[dcmdata['SeriesModule']['SeriesDescription']]
                else:
                    show_warning('One or more scan sets were not renamed, please check')
                MRGroup[dcmdata['StudyModule']['StudyInstanceUID']].append(examination)
        
                
            else:
                #probably a PETCT BUG
                #fails for diagnostic CTs
        
                if examination.EquipmentInfo.Modality=='CT':
                    scanType = 'CTFromPET'
                else:
                    scanType = 'PET'
                ending = ''
                ScanName = self.examination_name(examination, scanType,ending)
        
                PETGroup[dcmdata['StudyModule']['StudyInstanceUID']].append(examination)
            
            
            self.examination_name(examination, scanType,ending)
        
        #Group the appropriate Scans
        for StudyInstanceUID, groupList in MRGroup.items():
            if len(groupList)>1:
        
                nameList = [exam.Name for exam in groupList]
                MRGroupName = self.examination_name(groupList[0], 'TPMR',ending ='', change_name = 0 )
                if MRGroupName in self.case.ExaminationGroups.Keys:
                    self.warnings.append(MRGroupName+ ' already created, maybe multiple MR scans on same day or already created')
                    
                else:   
                    self.case.CreateExaminationGroup(ExaminationGroupName=MRGroupName, 
                                                     ExaminationGroupType="CollectionMrProtocol",
                                                     ExaminationNames=nameList)
        
        for StudyInstanceUID, groupList in PETGroup.items():
            if len(groupList)>1:
                nameList = [exam.Name for exam in groupList]
                PetGroupName = self.examination_name(groupList[0], 'PET',ending ='', change_name = 0 )
                if PetGroupName in self.case.ExaminationGroups.Keys:
                    self.warnings.append(PetGroupName+ ' already created, maybe multiple PET scans on same day or already created')
                else: 
                    self.case.CreateExaminationGroup(ExaminationGroupName=PetGroupName, 
                                                     ExaminationGroupType="CollectionMrProtocol", 
                                                     ExaminationNames=nameList)
        self.QA_patient_demographics()
        QCMessage = ''
        if len(self.warnings):
            QCMessage = '\n Warning: '.join(self.warnings)
        
            await_user_input(QCMessage+  '\n Please Review Names of Scans \n when completed press play again (lower left corner of script execution)')

    def QA_patient_demographics(self):
        N = self.patient.Name
        
        if len(N.split('^'))!= 2:
            self.warnings.append('Patient Needs first and last name')
        
            
        for letter in N.lower():
            if not letter in 'abcdefghijklmnopqrstuvwxyz^':
                self.warnings.append('special characters or spaces in name')
                
        if len(self.patient.PatientID)!=8:
            self.warnings.append('MRN wrong length')
            
        if not self.patient.PatientID.isnumeric():
            
            self.warnings.append('MRN is not numeric %s' %self.patient.PatientID)
            
        if self.patient.DateOfBirth == None:
            self.warnings.append('Patient has no date of birth')
            
        if not self.patient.Gender in ['Male', 'Female']:
            self.warnings.append('please select male or female gender (While Raystation is woke, Precision is not and will throw shade at the non-binary)')
            
            
        
        

    def examination_name(self,examination,scanType,ending = '',change_name = 1):
        months = ['JAN','FEB','MAR',"APR","MAY",'JUN','JUL','AUG','SEP', 'OCT',
             'NOV','DEC']
        DT = examination.GetExaminationDateTime()
         
        new_exam_name = '%s%2.2d%s%d%s'%(scanType,DT.Day, months[DT.Month-1],DT.Year, ending)
        if change_name:
            try:
                examination.Name = new_exam_name
            except Exception as e:
                print('Two scans of same name probably')
                new_exam_name = examination.Name
        return new_exam_name


    def detect_tags(self,dcmdata,tags):
        return sum([t in dcmdata['SeriesModule']['SeriesDescription'] for 
                    t in tags] ) 



    def find_TPCT(self):
        ##Look for the most recent examination
        
        TPCT_candidates = [exam for exam in self.case.Examinations 
                           if exam.GetAcquisitionDataFromDicom()['EquipmentModule']['StationName'] 
                           in self.CTSimulators]
        
        exam_dates = [exam.GetExaminationDateTime() for exam in TPCT_candidates]
        if len(exam_dates) == 0:
            self.warnings.append('Could not Find TPCT, please select TPCT as current Primary image in Image set library(patient modelling) ')
            return -1
        most_recent_date = max(exam_dates).Date
        
        TPCT_candidates = [TPCT_candidates[i] for i, d in enumerate(exam_dates)
                           if d.Date == most_recent_date]
        
        
        ##if still than more candidate, look for OMAR scans
        if len(TPCT_candidates) >1:
            OMR_candidates = []
            for exam in TPCT_candidates:
                dcmdata = exam.GetAcquisitionDataFromDicom()
                
                if self.detect_tags(dcmdata,tags = ['O-MAR','OMR','OMAR']):
                    OMR_candidates.append(exam)
            
            if len(OMR_candidates):
                TPCT_candidates = OMR_candidates
        
        ##If still more than one candidate, look for veinous scans     
        if len(TPCT_candidates)>1:
            venous_Candidates = []
            for exam in TPCT_candidates:
                dcmdata = exam.GetAcquisitionDataFromDicom()
                
                isVen = sum([OMRtag in dcmdata['SeriesModule']['SeriesDescription'] for 
                             OMRtag in ['Venous']] ) 
               
                if isVen:
                    venous_Candidates.append(exam)
            
            if len(venous_Candidates):
                TPCT_candidates = venous_Candidates
        
        
        if len(TPCT_candidates)>1:
            self.warnings.append('More than one plausible TPCT, please ensure that correct one is set as primary')
        return TPCT_candidates[0]

    def QC_TPCT_date(self,exam):
        '''Given an exam, determine whether it is recent enough to be used as a TPCT'''
        d = exam.GetExaminationDateTime()
        scan_age = d.Today.Subtract(D).Days
        if scan_age>21:
            self.warnings.append("Most recent TPCT is %s days old"%scan_age)

def do_task(**options):
    rename_simulation_scans().rename_scans()














