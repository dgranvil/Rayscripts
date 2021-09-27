#This function assumes that the TPCT is current examination
#This will be enforced because the Set Primary CT script will be
#forced to run prior to any scripts in the import Role being executed

from connect import *
from collections import defaultdict


class register_images:
    def __init__(self):
        self.case = get_current("Case")
        self.ui = get_current('ui')
        self.TPCT = get_current("Examination")

        
    def perform_registration(self):
        ##Find unique frames of reference
        unique_setup_reference_points = defaultdict(list)
        for exam in self.case.Examinations:
            setup_uid = exam.EquipmentInfo.FrameOfReference
            if setup_uid != self.TPCT.EquipmentInfo.FrameOfReference:
                unique_setup_reference_points[setup_uid].append(exam.Name)

        if len(unique_setup_reference_points) == 0:
            show_warning('No scansets found for registration to TPCT. Image registration not performed.')
        #For each unique frame of reference, choose best scan in set 
        #to use for registration to primary CT
        #'Best' scan is T1 followed by T2 for MR, CT for PetCT,
        #and just the first scan in the sequence for other/unknown scan type
        for group in unique_setup_reference_points.keys():

            registration_exists = self.check_for_existing_registration(self.TPCT.EquipmentInfo.FrameOfReference,self.case.Examinations[unique_setup_reference_points[group][0]].EquipmentInfo.FrameOfReference)
            if registration_exists == True:
                show_warning('Registration already exists for scans ' + ', '.join(unique_setup_reference_points[group]) + '.\nNew registration not performed for these.\nDelete existing registration before trying again.')
            elif registration_exists == False:
                
                #Ask user to select scan only if there is more than one scan to choose from in the group
                if len(unique_setup_reference_points[group]) > 1:
                    registrationScan = self.user_registration_scan_choice_popup(group)
                else:
                    registrationScan = unique_setup_reference_points[group][0]


                self.case.ComputeRigidImageRegistration(FloatingExaminationName=registrationScan, 
                                                        ReferenceExaminationName=self.TPCT.Name,
                                                        UseOnlyTranslations=False,
                                                        HighWeightOnBones=False,
                                                        InitializeImages=True,
                                                        FocusRoisNames=[],
                                                        RegistrationName=None)
                self.ui.TitleBar.MenuItem['Patient modeling'].Button_Patient_modeling.Click()
                self.ui.TabControl_Modules.TabItem['Image registration'].Button_Image_registration.Click()
            else:
                show_warning('Registration already exists. New registration not performed.\nDelete existing registration before trying again.')
    
  

    def user_registration_scan_choice_popup(self, group):
        #scan_dict is dictionary in which the keys are the string to display in the
        #dropdown menu that describe the scans, and the values are the exam objects
        #
        #display_list is the list of keys (ie scan descriptors) in scan_dict
        scan_dict = {}
        display_list =['']
        months = ['JAN','FEB','MAR',"APR","MAY",'JUN','JUL','AUG','SEP', 'OCT',
             'NOV','DEC']
        for exam in self.case.Examinations:
            if exam.EquipmentInfo.FrameOfReference == group:
                dcmdata = exam.GetAcquisitionDataFromDicom()
                date_time = exam.GetExaminationDateTime()
                date = str(date_time.Day) +  months[date_time.Month] + str(date_time.Year)
                modality = exam.EquipmentInfo.Modality
                name = exam.Name
                description = dcmdata['SeriesModule']['SeriesDescription'] 
                key = '  '.join((date, modality, name, description))
                scan_dict[key] = exam
        
        #create the display list
        for key in scan_dict.keys():
            if key not in display_list:
                display_list.append(key)

        message = modality + ' ' + date + ' Group: Please select which scan to use for registration for this scan group.'
        registration_scan_popup = popup(message, options = display_list)
        registrationScan = scan_dict[registration_scan_popup['option']].Name
        return registrationScan

            
            
    def check_for_existing_registration(self, TPCT_FoR, scan_FoR):
        registration_pairs = [[registration.FromFrameOfReference, registration.ToFrameOfReference] for registration in self.case.Registrations]
        if [scan_FoR, TPCT_FoR] in registration_pairs:
            return True
        else:
            return False



def do_task(**options):
    register_images().perform_registration()




























