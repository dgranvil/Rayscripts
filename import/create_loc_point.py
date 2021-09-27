# Assumes current scan is TPCT 

from connect import *

class create_loc_point:

    def __init__(self):
        self.TPCT = get_current("Examination")
        self.case = get_current("Case")
        self.loc_point_name = self.find_current_loc_point()

    def create_point(self):
        '''Create a localization point if it does not exist,
         add point geometry defined by imaging centre for each exam'''

        for exam in self.case.Examinations:
            print(self.loc_point_name)
            if self.loc_point_name == None:

                default_loc_point_name = r'CTref'
                self.case.PatientModel.CreatePoi(Examination=exam,
                                                  Point=self.find_centre_of_image(exam),
                                                  Name=default_loc_point_name, 
                                                  Color="Yellow",
                                                  VisualizationDiameter=1, 
                                                  Type="LocalizationPoint")
                self.loc_point_name = default_loc_point_name

            else:    

                self.case.PatientModel.StructureSets[exam.Name].PoiGeometries[self.loc_point_name].Point = self.find_centre_of_image(exam)

   
    def find_current_loc_point(self):
        
        for POI in self.case.PatientModel.PointsOfInterest:
            if POI.Type == 'LocalizationPoint':
                loc_point_name = POI.Name
                break
        else:

            loc_point_name = None
        return loc_point_name  
        

    def find_centre_of_image(self, exam):
        dcmdata = exam.GetAcquisitionDataFromDicom()
        pixSize = exam.Series[0].ImageStack.PixelSize.y
        NumPix = exam.Series[0].ImageStack.NrPixels.y
        corner = exam.Series[0].ImageStack.Corner.y
        centreY = corner + 0.5*pixSize*NumPix
        Point={ 'x': 0, 'y': centreY, 'z': 0 }
        return Point



def do_task(**options):
	create_loc_point().create_point()