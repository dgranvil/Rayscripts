# -*- coding: utf-8 -*-
"""
Created on Mon Mar 22 14:52:03 2021

@author: bywilson
"""


from connect import *
import sys

class add_report_views:
    def __init__(self):
        # Access current plan and show the form
        try:
            self.plan = get_current('Plan')
        except:
            raise Exception('No Plan loaded. Select the Plan')
            sys.exit()
        self.case = get_current("Case")
        self.patient = get_current("Patient")
        self.examination = get_current("Examination")
        self.beam_set = get_current('BeamSet')
        
        
  
    
    def do_task(self):

        ##find all PTVs
        ROIs = self.case.PatientModel.RegionsOfInterest
        PTVs = set([ROI.Name for ROI in ROIs if ROI.Type =='Ptv'])
        
        
        #PTV naming tag not filled in import, go by name of structures
        _ = [PTVs.add(ROI.Name) for ROI in ROIs if 'ptv' in ROI.Name.lower()]        
        PTVs = list(PTVs)
        
        ##Find points assosciated with PTVs
        slice_thickness = float(self.examination.GetStoredDicomTagValueForVerification(Group = 0x0018, Element = 0x0050)['SliceThickness'])/10
        
        
        ##add points to selection
        z_slice_holder=set()

        for PTVname in PTVs: #each of the ROIs
            PTV = self.case.PatientModel.StructureSets[self.examination.Name].RoiGeometries[PTVname]
            if PTV.PrimaryShape != None: #if the ROI is not empty in this struct set
            
                PTV_works = PTV.PrimaryShape
                BBox = PTV.GetBoundingBox()
                
                zmin = int(round(BBox[0].z))
                zmax = int(round(BBox[1].z))
                L = int(abs(zmax-zmin)/slice_thickness)
                _ = [z_slice_holder.add(round(z,1)) for z in self.linspace(zmin, zmax, L)]
                   
                
        dummy_x=float(format(PTV_works.Contours[0][0].x, '.1f'))
        dummy_y=float(format(PTV_works.Contours[0][0].y, '.1f'))
        
        z_slice_final = sorted(list(z_slice_holder))
        points=[{'x': dummy_x, 'y': dummy_y, 'z':z} for z in z_slice_final]
        self.plan.SetReportViewPositions(Coordinates=points)



    def linspace(self, a, b, n=100):
        if n < 2:
            return b
        diff = (float(b) - a)/(n - 1)
        return [diff * i + a  for i in range(n)]

def do_task(**options):
    add_report_views().do_task()


# beam_set = get_current('BeamSet')
# clinic_db = get_current('ClinicDB')

# file_name = os.path.join(os.environ['TEMP'], 'BeamSetReport.pdf')

# # Access the first template for a plan report in the clinic database
# site_settings = clinic_db.GetSiteSettings()
# template = next(t for t in site_settings.ReportTemplates if t.Type == 'TreatmentPlanReport')

# try:
#     # Try to create report, do not ignore warnings
#     beam_set.CreateReport(templateName = template.Name, filename = file_name, ignoreWarnings = False)

# except (System.InvalidOperationException, SystemError) as e:

#     # Display the warnings to the user
#     print ('Someting went wrong: {0}'.format(e))
#     print ('Retry and ignore warnings.')

#     # Create report, ignore warnings
#     beam_set.CreateReport(templateName = template.Name, filename = file_name, ignoreWarnings = True)

