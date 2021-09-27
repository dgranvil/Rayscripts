"""
This attached script is provided as a tool and not as a RaySearch endorsed script for
clinical use.  The use of this script in its whole or in part is done so
without any guarantees of accuracy or expected outcomes. Please verify all results. Further,
per the Raystation Instructions for Use, ALL scripts MUST be verified by the user prior to
clinical use.

Change FoR v 0.1

This script will change the Frame of Reference for the selected Examination. It will not work if:

-The exam has been used to create a FoR Registration
-The exam is referenced in a structure registration (Rigid/Deformable)
-The exam is part of an examination group
-The exam is referenced by a treatment plan
-The exam has computed doses
"""

import clr, wpf

from connect import *

clr.AddReference('System')
clr.AddReference("System.Xml")
from System.Collections.ObjectModel import ObservableCollection
from System.IO import StringReader
from System.Windows import Window, MessageBox
from System.Windows.Controls import ComboBox, ComboBoxItem
from System.Xml import XmlReader

def main():
    global case
    case = get_current('Case')
    dialog = myWindow()
    dialog.ShowDialog()

class myWindow(Window):
    def __init__(self):
        self.xaml = xaml()
        xr = XmlReader.Create(StringReader(self.xaml.xaml))
        wpf.LoadComponent(self, xr)
        self.comboBox.ItemsSource = []
        self.comboBox.ItemsSource = self.get_exam_list()

    def comboBox_MouseLeave(self, sender, e):
        if self.comboBox.SelectedIndex != -1:
            self.CFoRbutton.IsEnabled = True
        else:
            self.CFoRbutton.IsEnabled = False

    def CFoRbutton_Click(self, sender, e):
        try:
            FoR_old = case.Examinations[self.comboBox.SelectedItem.Content].EquipmentInfo.FrameOfReference
            case.Examinations[self.comboBox.SelectedItem.Content].AssignToNewFrameOfReference()
            FoR_new = case.Examinations[self.comboBox.SelectedItem.Content].EquipmentInfo.FrameOfReference
            MessageBox.Show(
                "The FoR for exam:{0} has successfully been changed.\n\nOld FoR:    {1}\nNew FoR:    {2}".format(
                    self.comboBox.SelectedItem.Content,
                    FoR_old,
                    FoR_new
                ),
                "Success"
            )
            self.DialogResult = True
        except Exception, err:
            MessageBox.Show(
                "The FoR for exam:{0} has was not changed.\n\nPlease review the error message and make appropriate changes:\n{1}".format(
                    self.comboBox.SelectedItem.Content,
                    str(err)
                ),
                "Failure"
            )
            self.DialogResult = False


    def Cancelbutton_Click(self, sender, e):
        self.DialogResult = False

    def Window_MouseLeftButtonDown(self, sender, e):
        self.DragMove()

    def get_exam_list(self):
        exams = [e.Name for e in case.Examinations]
        exam_collection = ObservableCollection[ComboItems]()
        for e in sorted(exams):
            exam_collection.Add(ComboItems(e))
        return exam_collection

class ComboItems(ComboBoxItem):
  '''This class is necessary to add items to a WPF control'''

  def __init__(self,name):
    self.Content = name
    self.Font = 10

class xaml():
    def __init__(self):
        self.xaml = """
<Window
       xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
       xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
       Title="ChangeFOR" Height="137.677" Width="203.966" WindowStyle="None"  ResizeMode="NoResize"
             BorderThickness="1" WindowStartupLocation="CenterScreen" Background="#FF313131" BorderBrush="Black"
             MouseLeftButtonDown="Window_MouseLeftButtonDown">
    <Grid>
        <ComboBox x:Name="comboBox" HorizontalAlignment="Left" Margin="10,41,0,0" VerticalAlignment="Top" Width="176" MouseLeave="comboBox_MouseLeave"/>
        <Label x:Name="label" Content="Choose Examination to Change" HorizontalAlignment="Left" Margin="10,10,0,0" VerticalAlignment="Top" Foreground="#FFD9D9D9"/>
        <Button x:Name="CFoRbutton" Content="Change FoR" IsEnabled="False" HorizontalAlignment="Left" Margin="10,68,0,0" VerticalAlignment="Top" Width="75" Click="CFoRbutton_Click"/>
        <Button x:Name="Cancelbutton" Content="Cancel" HorizontalAlignment="Left" Margin="111,68,0,0" VerticalAlignment="Top" Width="75" Click="Cancelbutton_Click"/>
    </Grid>
</Window>
    """

def do_task(**options):
	create_loc_point().do_task()
if __name__ == '__main__':
    main()

    exit(0)