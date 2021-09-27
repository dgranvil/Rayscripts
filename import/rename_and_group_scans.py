
"""
To Do:
Make MRNamePairs exhaustive for all protocols used
"""

# Notes:
# Uses CTSim 'StationName' in examination.GetDataAcquisitionDataFromDicom()['StudyModule'] to determine if 
# image type = TPCT
#      -CTSimulators list contains StationName for each of the 3 CTSims
# 4DCT determined by 'E1 Linear' presence in tag
#
# Uses SeriesDescription' in examination.GetDataAcquisitionDataFromDicom()['SeriesModule'] to determine 
# type of MR sequence
#      -MRNamePairs dict contains key-value pairs of {'SeriesDescription' : ending to use in rename} for
#       each MR sequence
#
# Uses StudyInstanceUID to determine if image type is PetCT (ie a Modality = Pet and a Modality = CT)
# with same StudyInstanceUID

from connect import *
from collections import defaultdict

class rename_and_group_scans:

    
    ### Variables that should go in config
    MRNamePairs ={'SAG T1 SPACE':'ST1',  'AX T2 BLADE SPAIR (3mm)':'T2B' , 'AX VIBE DIXON':'VBC' }
    CTSimulators = ['HOST-76205','HOST-7055','PHILIPS-7055']
    MRSimulators = ['AWP42514']
    TomoUnits = ['0210511',' 0210266']

    
    def __init__(self):
        
        self.case = get_current("Case")
        
        
    def perform_renaming_and_grouping(self):

       
        # Create empty default dicts to append to if MR, PET, or 4D scans detected
        # These are the 3 types of imagesets that can be 'grouped' in RayStation
        MRGroup = defaultdict(list)
        PETGroup = defaultdict(list)
        CT4DGroup = defaultdict(list)
        

        # Loop over all examinations
        # If exam is a TPCT (ie if StationName in CTSimulators)
        #      Rename to TPCT + ending (venour, arterial, omar, mip, aip, or phase currently supported)
        for exam_number , examination in enumerate(self.case.Examinations):
            scanType = ''
            dcmdata = examination.GetAcquisitionDataFromDicom()
            StationName = dcmdata['EquipmentModule']['StationName']
            ending = str(exam_number)
            if StationName in self.CTSimulators:
                scanType = 'TPCT'
                ending = ''
                
                if self.detect_tags(dcmdata, tags = ['Venous']):
                    ending += '_VEN'
                elif self.detect_tags(dcmdata, tags = ['Arterial']):
                    ending += '_ART'
                elif self.detect_tags(dcmdata, tags = ['O-MAR','OMR','OMAR']):
                    ending += '_OMR'
                elif self.detect_tags(dcmdata, tags = ['MIP']):
                    ending += '_MIP'
                    CT4DGroup[dcmdata['StudyModule']['StudyInstanceUID']].append(examination)
                elif self.detect_tags(dcmdata, tags = ['AIP']):
                    ending += '_AIP'
                    CT4DGroup[dcmdata['StudyModule']['StudyInstanceUID']].append(examination)
                elif self.detect_tags(dcmdata, tags = ['E1 Linear']):
                    if dcmdata['SeriesModule']['SeriesDescription'][0:2] == '0%':
                        ending += '_P0'
                        CT4DGroup[dcmdata['StudyModule']['StudyInstanceUID']].append(examination)
                    else: 
                        ending += '_P' + dcmdata['SeriesModule']['SeriesDescription'][0:2]
                        CT4DGroup[dcmdata['StudyModule']['StudyInstanceUID']].append(examination)
                elif self.detect_tags(dcmdata, tags = ['DIBH']):
                    ending += '_DIBH'
                elif self.detect_tags(dcmdata, tags = ['FB']):
                    ending += '_FB'

            elif StationName in self.TomoUnits:
            	scanType = 'MVCT'
            	ending = ''

            # If exam is an MR
            #     If StationName is our MRSim, then name 'TPMR'
            #     If any other MR, then name 'MR'
            elif examination.EquipmentInfo.Modality=='MR':

                if StationName in self.MRSimulators:            
                    scanType = 'TPMR'
                else:
                    scanType = 'MR'
                # Determine type of MR scan for renaming, based on MRNamePairs dict
                if dcmdata['SeriesModule']['SeriesDescription'] in self.MRNamePairs:
                    ending = self.MRNamePairs[dcmdata['SeriesModule']['SeriesDescription']]
                else:
                    show_warning('One or more MR scan sets were not renamed, please check')
                MRGroup[dcmdata['StudyModule']['StudyInstanceUID']].append(examination)
       
            
            # If a CT from PETCT scan, then name 'CTFromPET'
            # Otherwise, name 'CT' 
            elif examination.EquipmentInfo.Modality=='CT':
                # Check of there is a PET with same Frame of Reference to ensure
                # that this is a CT from PET
                FoR_UID = examination.EquipmentInfo.FrameOfReference
                for other_exam in self.case.Examinations:
                    if other_exam.EquipmentInfo.Modality == 'Pet' and other_exam.EquipmentInfo.FrameOfReference == FoR_UID:
                        scanType = 'CTFromPET'
                        PETGroup[dcmdata['StudyModule']['StudyInstanceUID']].append(examination)
                        PETGroup[dcmdata['StudyModule']['StudyInstanceUID']].append(other_exam)
                
                if scanType != 'CTFromPET':
                    #name as 'CT' (CT that is not from our CTSims, or from PETCT)
                    scanType = 'CT'
                ending = ''
                
            elif examination.EquipmentInfo.Modality == 'Pet':
                scanType = 'PET'
                ending = ''
            

            self.examination_name(examination, scanType, ending)


        self.perform_scan_grouping(MRGroup, 'CollectionMrProtocol')
        self.perform_scan_grouping(CT4DGroup, 'Collection4dct')
        self.perform_scan_grouping(PETGroup, 'PetCT')


    #group_dict = default_dict (MRGroup, PETGroup, or CT4DGroup)
    #group_type = RayStation option in case.ExeminationGroupType method - either CollectionMrProtocol, PetCT, or Collection4dct)
    def perform_scan_grouping(self, group_dict, group_type):
        for StudyInstanceUID, groupList in group_dict.items():
            if len(groupList)>1:
                nameList = [exam.Name for exam in groupList]

                if group_type == 'CollectionMrProtocol':
                    scanType = 'TPMR'
                elif group_type == 'PetCT':
                    scanType = 'PETCT'
                elif group_type == 'Collection4dct':
                    scanType = '4DCT'

                group_name = self.examination_name(groupList[0], scanType, ending ='', change_name = 0 )

                if group_name in self.case.ExaminationGroups.Keys:
                    pass #group already exists
                else:   
                    self.case.CreateExaminationGroup(ExaminationGroupName=group_name, 
                                                      ExaminationGroupType=group_type,
                                                      ExaminationNames=nameList)


    def examination_name(self,examination,scanType,ending = '',change_name = 1):
        months = ['JAN','FEB','MAR',"APR","MAY",'JUN','JUL','AUG','SEP', 'OCT',
             'NOV','DEC']
        DT = examination.GetExaminationDateTime()
         
        new_exam_name = '%s%2.2d%s%d%s'%(scanType,DT.Day, months[DT.Month-1],DT.Year, ending)
        print('new name', new_exam_name, scanType, ending)
        if change_name:
            try:
                examination.Name = new_exam_name
            except Exception as e:
                show_warning('Unable to correctly rename scan ' + examination.Name + '. This is likely due to multiple scans of the same type on the same day. Please rename manually.' )
                new_exam_name = examination.Name
        return new_exam_name


    def detect_tags(self,dcmdata,tags):
        return sum([t in dcmdata['SeriesModule']['SeriesDescription'] for 
                    t in tags] ) 


def do_task(**options):
    rename_and_group_scans().perform_renaming_and_grouping()













