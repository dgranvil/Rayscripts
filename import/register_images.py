#This function assumes that the TPCT is current examination
#Currently use await_user_input to have user verify this, and the existing reg check but it doesn't work well because it shows up behind Rayscripts gui
#Ryan working on features that will improve this
#Need to check for petCT and other imaging modality bugs


from connect import *
from collections import defaultdict

#warnings = ['TPCT must be current examination before running this script.']

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
        print(unique_setup_reference_points)

        #For each unique frame of reference, choose best scan in set 
        #to use for registration to primary CT
        #'Best' scan is T1 followed by T2 for MR, CT for PetCT,
        #and just the first scan in the sequence for other/unknown scan type
        for Scans in unique_setup_reference_points.values():
                       
            #First determine scan type (ie MR, PetCT, or other)
            for scan in Scans:
                registration_exists = self.check_for_existing_registration(self.TPCT.EquipmentInfo.FrameOfReference,self.case.Examinations[scan].EquipmentInfo.FrameOfReference)
                print(registration_exists)
                if registration_exists == True:
                    break
                elif registration_exists == False:

                    if self.case.Examinations[scan].EquipmentInfo.Modality == 'MR':
                        scanType = 'MR'
                        bestImages = ['T1', 'T2']
                        registrationScan = self.find_registration_scan(bestImages, Scans, scanType)
                        break
                    elif self.case.Examinations[scan].EquipmentInfo.Modality == 'Pet':
                        scanType = 'PetCT'
                        bestImages = ['CTFromPET']
                        registrationScan = self.find_registration_scan(bestImages, Scans, scanType)
                        break
                    else:
                        scanType = 'Unknown'
                        registrationScan = Scans[0]
                    
            
            if registration_exists == False:
                self.case.ComputeRigidImageRegistration(FloatingExaminationName=registrationScan, 
                                                        ReferenceExaminationName=self.TPCT.Name,
                                                        UseOnlyTranslations=False,
                                                        HighWeightOnBones=False,
                                                        InitializeImages=True,
                                                        FocusRoisNames=[],
                                                        RegistrationName=None)
                self.ui.TitleBar.MenuItem['Patient modeling'].Button_Patient_modeling.Click()
                self.ui.TabControl_Modules.TabItem['Image registration'].Button_Image_registration.Click()
                show_warning('Please check the registration before continuing')
            else:
                show_warning('Registration already exists. New registration not performed.\nDelete existing registration before trying again.')
    


    def find_registration_scan(self, bestImages, Scans, scanType):
        for bestImage in bestImages:
            for scan in Scans:
                if scanType == 'MR':
                    print('dal', bestImage, self.case.Examinations[scan].GetAcquisitionDataFromDicom()['SeriesModule']['SeriesDescription'] )
                    if bestImage in self.case.Examinations[scan].GetAcquisitionDataFromDicom()['SeriesModule']['SeriesDescription']:
                        registrationScan = scan                 
                        break
                elif scanType == 'Pet':
                    if bestImage in self.case.Examinations[scan].EquipmentInfo.Modality:
                        registrationScan = scan
                        break
        return registrationScan     
            
            
            
    def check_for_existing_registration(self, TPCT_FoR, scan_FoR):
        registration_pairs = [[registration.FromFrameOfReference, registration.ToFrameOfReference] for registration in self.case.Registrations]
        if [scan_FoR, TPCT_FoR] in registration_pairs:
            return True
        else:
            return False



def do_task(**options):
    register_images().perform_registration()




























