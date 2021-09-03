# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 17:31:10 2021

@author: bywilson
"""

# from connect import *

# class create_dose_composite():
#     def create_hybrid_registration():
        
from connect import *


class rigid_registration_hack:
    
    def __init__(self):

        self.case = get_current("Case")
        # self.beam_set = get_current("BeamSet")
        self.examination = get_current("Examination")
        self.create_externals()
 
        hack_roi_name = r'registration_hack'
        roi_names = [ROI.Name for ROI in self.case.PatientModel.RegionsOfInterest]
        if hack_roi_name in roi_names:
            #delete roi
            self.case.PatientModel.RegionsOfInterest[hack_roi_name].DeleteRoi()
            
        hack_roi = self.case.PatientModel.CreateRoi(Name=hack_roi_name, Color="Red", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
        
        #create a sphere located at the corner bounding box of the external in the lateral directions, and the central slice
        external = self.external
        external_geometry = self.case.PatientModel.StructureSets[self.examination.Name].RoiGeometries[self.external.Name]
        BB = external_geometry.GetBoundingBox()     

        dxy = 1
        centre = dict()
        centre['z'] = round((BB[0].z + BB[1].z)/2)
        centre['x'] = BB[0].x + dxy 
        centre['y'] = BB[0].y +dxy

        
        hack_roi.CreateSphereGeometry(Radius = 0.75,Examination = self.examination, Center = centre, Representation = 'Voxels' )
        
        ##Create deformation
        #Find examination pairs with rigid registrations
        rigid_registration_exam_pairs = []
        need_hack_roi = set()
        for reg in self.case.Registrations:
            exam_list = self.case.Examinations
            from_exam = exam_list[reg.RegistrationSource.FromExamination.Name]
            to_exam = exam_list[reg.RegistrationSource.ToExamination.Name]
            need_hack_roi.add(reg.RegistrationSource.ToExamination.Name)
            rigid_registration_exam_pairs.append(
                [from_exam, to_exam])
            
        
        self.case.PatientModel.CopyRoiGeometries(SourceExamination=self.examination, TargetExaminationNames=list(need_hack_roi), RoiNames=[hack_roi_name])
        print(rigid_registration_exam_pairs)
        for pair in rigid_registration_exam_pairs:
            self.case.PatientModel.CreateHybridDeformableRegistrationGroup(
                RegistrationGroupName=self.registration_name(pair[0].Name, pair[1].Name), 
                ReferenceExaminationName=pair[0].Name, 
                TargetExaminationNames=[pair[1].Name], ControllingRoiNames=[hack_roi_name],
                ControllingPoiNames=[], FocusRoiNames=[],
                AlgorithmSettings={ 'NumberOfResolutionLevels': 3, 'InitialResolution': { 'x': 0.5, 'y': 0.5, 'z': 0.5 }, 
                                   'FinalResolution': { 'x': 0.25, 'y': 0.25, 'z': 0.3 }, 
                                   'InitialGaussianSmoothingSigma': 2, 'FinalGaussianSmoothingSigma': 0.333333333333333,
                                   'InitialGridRegularizationWeight': 400, 'FinalGridRegularizationWeight': 400,
                                   'ControllingRoiWeight': 0.5, 'ControllingPoiWeight': 0.1, 'MaxNumberOfIterationsPerResolutionLevel': 1000,
                                   'ImageSimilarityMeasure': "None", 'DeformationStrategy': "Default", 'ConvergenceTolerance': 1E-05 })

    def registration_name(self,E1,E2):
        return 'rigid'+E1 +'to'+E2
    
    
    def create_externals(self):
        #find external-type structure if it exists, if doesnt, create
        external = 0 
        for ROI in self.case.PatientModel.RegionsOfInterest:
            if ROI.Type == 'External':
                external = ROI
        if external == 0:#create external
            external = self.case.PatientModel.CreateRoi(Name=r"External", Color="Green", Type="External", TissueName=r"", RbeCellTypeName=None, RoiMaterial=None)
        
        externals_to_contour = [exam for exam in self.case.Examinations
                                if not self.case.PatientModel.StructureSets[exam.Name].RoiGeometries[external.Name].HasContours()]
        for exam in externals_to_contour:
            external.CreateExternalGeometry(Examination=exam, ThresholdLevel=-250)
        self.external = external

def do_task(**options):
    rigid_registration_hack()

if __name__ == '__main__':
    rigid_registration_hack()


        
 