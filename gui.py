

import vtk 
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
import vtk.util.numpy_support

from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QSlider, QGridLayout, QLabel, QPushButton, QTextEdit
import PyQt6.QtCore as QtCore
from PyQt6.QtCore import Qt


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName('Main Window')
        MainWindow.setWindowTitle('Mantle Convection Visualization')

        # Central Widget
        self.centralWidget = QWidget(MainWindow)

        self.gridlayout = QGridLayout(self.centralWidget)
        self.vtkWidget = QVTKRenderWindowInteractor(self.centralWidget)

        # Grid layout here.
        self.gridlayout.addWidget(self.vtkWidget, 0, 0, 24, 34)
        self.gridlayout.addWidget(self.camera_button, 0, 34, 24, 2)

        MainWindow.setCentralWidget(self.centralWidget)
        
        
class MantleVis_GUI(QMainWindow):

    def __init__(self, parent = None): 
        QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Create the Renderer
        self.ren = vtk.vtkRenderer()
        self.ren.GradientBackgroundOn()  # Set gradient for background
        self.ren.SetBackground(0.7, 0.7, 0.7)  # Set background color

        self.iren = self.ui.vtkWidget.GetRenderWindow().GetInteractor()
        self.iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.ui.vtkWidget.GetRenderWindow().AddRenderer(self.ren)

    # Load in the dataset and create visualization pipeline
    def load_data(self, filename):
        # reader = vtk.vtkXMLUnstructuredGridReader()       # For .vtu files
        reader = vtk.vtkNetCDFReader()                      # For .nc  files
        reader.SetFileName(filename)
        reader.Update()

        self.ren.AddActor(...)

    def set_camera(self, cam_file):
        # Setup camera if it is set
        if cam_file is not None:
            camera = vtk_camera.load_camera(cam_file)
            self.ren.SetActiveCamera(camera)

    def display(self):
        self.ui.vtkWidget.GetRenderWindow().SetSize([1024, 768])
        self.show()
        self.setWindowState(Qt.WindowState.WindowMaximized)  # Maximize the window
        self.iren.Initialize() # Need this line to actually show
                                # the render inside Qt
        