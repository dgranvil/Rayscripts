# need to sort the keys in the list presented
from connect import * 

warnings  = ['This script must be run prior to running any others.\nUnchecking will be disabled in future.']

class determine_tpct:
    ### Variables that should go in config
    MRNamePairs ={'SAG T1 SPACE':'ST1',  'AX T2 BLADE SPAIR (3mm)':'T2B' , 'AX VIBE DIXON':'VBC' }
    CTSimulators = ['HOST-76205','HOST-7055','PHILIPS-7055']
    MRSimulators = ['AWP42514']

    def __init__(self):
        self.case = get_current('Case')

    def guess_TPCT(self):
        
        TPCT_candidates = [exam for exam in self.case.Examinations 
                           if exam.GetAcquisitionDataFromDicom()['EquipmentModule']['StationName'] 
                           in self.CTSimulators]
        
        exam_dates = [exam.GetExaminationDateTime() for exam in TPCT_candidates]
        if len(exam_dates) == 0:
            return -1
        
        else:
            most_recent_date = max(exam_dates).Date
            
            TPCT_candidates = [TPCT_candidates[i] for i, d in enumerate(exam_dates)
                               if d.Date == most_recent_date]
            
            
            ##if still than more than 1 candidate, look for OMAR scans
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
            
            # If there's still more than 1 candidate maybe it's 4D, look for AIP
            if len(TPCT_candidates)>1:
                ct4d_candidates = []
                for exam in TPCT_candidates:
                    dcmdata = exam.GetAcquisitionDataFromDicom()
                    if self.detect_tags(dcmdata, tags = ['AIP']):
                        ct4d_candidates.append(exam)
                if len(ct4d_candidates):
                    TPCT_candidates = ct4d_candidates

            # Lastly, look for DIBH/FB
            if len(TPCT_candidates) > 1:
                dibh_candidates = []
                for exam in TPCT_candidates:
                    dcmdata = exam.GetAcquisitionDataFromDicom()
                    if self.detect_tags(dcmdata, tags = ['DIBH']):
                        dibh_candidates.append(exam)
                if len(dibh_candidates):
                    TPCT_candidates = dibh_candidates

            if len(TPCT_candidates)>1:
                return -1
            else:
                return TPCT_candidates[0]

    def user_tpct_choice_popup(self, best_guess_tpct):
        #scan_dict is dictionary in which the keys are the string to display in the
        #dropdown menu that describe the scans, and the values are the exam objects
        #
        #display_list is the list of keys (ie scan descriptors) in scan_dict
        #the first value of display_list is blank if an appropriate tpct isn't
        #autodetected. Otherwise, the autodetected TPCT is the first scan.
        scan_dict = {}
        display_list =['']
        months = ['JAN','FEB','MAR',"APR","MAY",'JUN','JUL','AUG','SEP', 'OCT',
             'NOV','DEC']
        for exam in self.case.Examinations:
            dcmdata = exam.GetAcquisitionDataFromDicom()
            date_time = exam.GetExaminationDateTime()
            date = str(date_time.Day) +  months[date_time.Month] + str(date_time.Year)
            modality = exam.EquipmentInfo.Modality
            name = exam.Name
            description = dcmdata['SeriesModule']['SeriesDescription'] 
            key = '  '.join((date, modality, name, description))
            scan_dict[key] = exam
            #if best guess tpct is found, and this is it, then make it first in the list to display
            if best_guess_tpct != -1:
                if exam.Name == best_guess_tpct.Name:
                    display_list[0] = key
        
        #create the display list
        for key in scan_dict.keys():
            if key not in display_list:
                display_list.append(key)

        #display different messages depending on whether tpct is auto detected
        if best_guess_tpct == -1:
            message = 'TPCT candidate not found.\n\nPlease select Primary TPCT image set from the drop down menu below.'
        else:
            message = 'The image set below has been automatically detected as the Primary TPCT.\n\nIf this is not correct, please change it in the dropdown menu below.'
        tpct_popup = popup(message, options = display_list)
        selected_tpct = scan_dict[tpct_popup['option']]
        selected_tpct.SetPrimary()


    def detect_tags(self,dcmdata,tags):
        return sum([t in dcmdata['SeriesModule']['SeriesDescription'] for 
                    t in tags] ) 

def do_task(**options):
    best_guess_TPCT = determine_tpct().guess_TPCT()
    determine_tpct().user_tpct_choice_popup(best_guess_tpct = best_guess_TPCT)


