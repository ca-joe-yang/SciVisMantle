from PyQt5.QtWidgets import \
    QWidget, QMainWindow, QGridLayout, \
    QPushButton, QTextEdit, QColorDialog
from PyQt5.QtGui import QColor
# import PyQt5.QtCore as QtCore
from PyQt5.QtCore import Qt

from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk

import sys
from .vtk_helper import vtk_camera
from .axes import Axes

class UiBase: 

    def setupUi(self, window, resolution=(1280, 768)):
        # in Qt, windows are made of widgets.
        # centralWidget will contains all the other widgets
        self.centralWidget = QWidget(window)
        # we will organize the contents of our centralWidget
        # in a grid / table layout
        # Here is a screenshot of the layout:
        # https://www.cs.purdue.edu/~cs530/projects/img/PyQtGridLayout.png
        self.gridlayout = QGridLayout(self.centralWidget)
        # vtkWidget is a widget that encapsulates a vtkRenderWindow
        # and the associated vtkRenderWindowInteractor. We add
        # it to centralWidget.
        self.vtkWidget = QVTKRenderWindowInteractor(self.centralWidget)
        self.gridlayout.addWidget(self.vtkWidget, 0, 0, 7, 4)

        # Push buttons
        self.push_screenshot = QPushButton()
        self.push_screenshot.setText('Save screenshot')
        self.push_camera = QPushButton()
        self.push_camera.setText('Save camera info')
        self.push_quit = QPushButton()
        self.push_quit.setText('Quit')

        # Text windows
        self.camera_info = QTextEdit()
        self.camera_info.setReadOnly(True)
        self.camera_info.setAcceptRichText(True)
        self.camera_info.setHtml("<div style='font-weight: bold'>Camera settings</div>")
        self.log = QTextEdit()
        self.log.setReadOnly(True)

        # We are now going to position our widgets inside our
        # grid layout. The top left corner is (0,0)
        #       0         1         2        3          4
        #     -----------------------------------------------------
        #  0  |                                     | Push Button |
        #     |                                     ---------------
        #  1  |                                     | Push Button |
        #     |                                     ---------------
        #  2  |                                     | Push Button |
        #     |                                     ---------------
        #  3  |                                     | Text        |
        #  4  |                                     |    Window   |
        #     |                                     ---------------
        #  5  |                                     | Text        |
        #  6  |                                     |    Window   |
        #     -----------------------------------------------------
        #  7  | Label | Slider  | Label | Slider    | Push Button |
        #     -----------------------------------------------------
        #  8  | Label | Slider  |       |           |             |
        #     -----------------------------------------------------

        self.gridlayout.addWidget(self.push_screenshot, 0, 4, 1, 1)
        self.gridlayout.addWidget(self.push_camera, 1, 4, 1, 1)
        self.gridlayout.addWidget(self.camera_info, 2, 4, 1, 2)
        self.gridlayout.addWidget(self.log, 3, 4, 1, 2)
        self.gridlayout.addWidget(self.push_quit, 6, 4, 1, 1)

        window.setCentralWidget(self.centralWidget)

        self.vtkWidget.GetRenderWindow().SetSize(*resolution)
        self.log.insertPlainText('Set render window resolution to {}\n'.format(resolution))

class PyQtBase(QMainWindow):

    def __init__(self, output, verbose=True):
        super().__init__()
        self.ui = None

        self.frame_counter = 0
        self.verbose = verbose
        self.output = output

        self.colors = vtk.vtkNamedColors()

        self.axes = Axes()
        self.show_axes = True

    def set_callback(self):
        self.ui.push_screenshot.clicked.connect(self.screenshot_callback)
        self.ui.push_camera.clicked.connect(self.camera_callback)
        self.ui.push_quit.clicked.connect(self.quit_callback)

    def run(self):
        self.show()
        self.setWindowState(Qt.WindowMaximized)  # Maximize the window
        self.iren.Initialize() # Need this line to actually show
                                # the render inside Qt

    def screenshot_callback(self):
        self.save_frame()

    def camera_callback(self):
        self._print_camera_settings()

    def quit_callback(self):
        sys.exit()

    def save_frame(self, filename=None):
        window = self.ui.vtkWidget.GetRenderWindow()
        log = self.ui.log
        # ---------------------------------------------------------------
        # Save current contents of render window to PNG file
        # ---------------------------------------------------------------
        if filename is None:
            filename = f'{self.output}-{self.frame_counter:05d}.png'
        image = vtk.vtkWindowToImageFilter()
        image.SetInput(window)
        png_writer = vtk.vtkPNGWriter()
        png_writer.SetInputConnection(image.GetOutputPort())
        png_writer.SetFileName(filename)
        window.Render()
        png_writer.Write()
        self.frame_counter += 1
        if self.verbose:
            print(filename + " has been successfully exported")
        log.insertPlainText('Exported {}\n'.format(filename))

    def _print_camera_settings(self):
        # ---------------------------------------------------------------
        # Print out the current settings of the camera
        # ---------------------------------------------------------------
        camera = self.ren.GetActiveCamera()
        text_window = self.ui.camera_info
        log = self.ui.log
        text_window.setHtml("<div style='font-weight:bold'>Camera settings:</div><p><ul><li><div style='font-weight:bold'>Position:</div> {0}</li><li><div style='font-weight:bold'>Focal point:</div> {1}</li><li><div style='font-weight:bold'>Up vector:</div> {2}</li><li><div style='font-weight:bold'>Clipping range:</div> {3}</li></ul>".format(camera.GetPosition(), camera.GetFocalPoint(),camera.GetViewUp(),camera.GetClippingRange()))
        log.insertPlainText('Updated camera info\n')

        camera_filename = self.output + '_camera.json'
        vtk_camera.save_camera(camera, filename=camera_filename)
        log.insertPlainText(f'Saved camera settings to {camera_filename}\n')

    def load_camera(self, camera=None):
        if camera is not None:
            self.ren.SetActiveCamera(vtk_camera.load_camera(camera))

    def Update(self):
        self.ui.vtkWidget.GetRenderWindow().Render()