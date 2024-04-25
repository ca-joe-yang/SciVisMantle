from PyQt5.QtWidgets import \
    QWidget, QMainWindow, QGridLayout, \
    QPushButton, QTextEdit, QColorDialog, \
    QSlider, QLineEdit, QLabel, \
    QListWidget, QListWidgetItem, QScrollBar
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk

import sys
from .vtk_helper import vtk_camera
from .axes import Axes

from .utils import GetViewRight

class MyQTextEdit:

    def __init__(self, name, val, gridlayout, col_idx=0):
        self.val = val

        self.label = QLabel()
        self.label.setText(f'{name}: ')

        self.input = QLineEdit()
        self.input.setText(str(self.val))

        self.button = QPushButton()
        self.button.setText('Update')

        gridlayout.addWidget(self.label, col_idx, 0, 1, 1)
        gridlayout.addWidget(self.input, col_idx, 1, 1, 1)
        gridlayout.addWidget(self.button, col_idx, 2, 1, 1)

    def set_callback(self, callback):
        self.button.clicked.connect(callback)

    def Update(self):
        self.val = int(self.input.text())
        return self.val

class MyQList:

    def __init__(self, fields):
        self.fields_list = QListWidget()
        for i, f in enumerate(fields):
            item = QListWidgetItem(f)
            self.fields_list.addItem(item)
            if i == 0:
                # item.setSelected(True)
                self.fields_list.setCurrentItem(item)

        # self.scroll_bar = QScrollBar()
        
        # self.fields_list.setVerticalScrollBar(self.scroll_bar)
        # self.scroll_bar.setValue(0)

        # Get vertical scrollbar of QListWidget
        self.scrollbar = self.fields_list.verticalScrollBar()

        # Set scrollbar value to the calculated value
        self.scrollbar.setValue(0)

        # self.label = QLabel()
 

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
        self.push_reset = QPushButton()
        self.push_reset.setText('Reset camera')
        self.push_camera = QPushButton()
        self.push_camera.setText('Save camera info')
        self.push_start = QPushButton()
        self.push_start.setText('Start')
        self.push_quit = QPushButton()
        self.push_quit.setText('Quit')

        self.push_clipY = QPushButton()
        self.push_clipY.setText('Update')

        # Text windows
        self.camera_info = QTextEdit()
        self.camera_info.setReadOnly(True)
        self.camera_info.setAcceptRichText(True)
        self.camera_info.setHtml("<div style='font-weight: bold'>Camera settings</div>")
        self.log = QTextEdit()
        self.log.setReadOnly(True)

        self.l_field = MyQList(['temperature', 'anomaly'])
        self.r_field = MyQList(['temperature', 'anomaly'])
        

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
        #  7  | Label | Value  | Update |     | Push Button |
        #     -----------------------------------------------------
        #  8  | Label | Value  | Update |           |             |
        #     -----------------------------------------------------

        self.gridlayout.addWidget(self.push_screenshot, 0, 4, 1, 1)
        self.gridlayout.addWidget(self.push_start, 1, 4, 1, 1)
        self.gridlayout.addWidget(self.push_reset, 2, 4, 1, 1)
        self.gridlayout.addWidget(self.push_camera, 3, 4, 1, 1)
        self.gridlayout.addWidget(self.camera_info, 4, 4, 1, 1)
        self.gridlayout.addWidget(self.log, 5, 4, 1, 1)
        self.gridlayout.addWidget(self.push_quit, 6, 4, 1, 1)
        
        self.gridlayout.addWidget(self.l_field.fields_list, 7, 0, 1, 2)
        self.gridlayout.addWidget(self.r_field.fields_list, 7, 2, 1, 2)
        
        # self.gridlayout.addWidget(self.push_toggle3, 9, 1, 1, 1)

        # self.gridlayout.addWidget(self.slider_clipX, 7, 2, 1, 1)
        # self.gridlayout.addWidget(self.input_clipY, 8, 1, 1, 1)
        # self.gridlayout.addWidget(self.push_clipY, 8, 2, 1, 1)
        # self.gridlayout.addWidget(self.slider_clipZ, 9, 2, 1, 1)

        # self.slider_clipX.setValue(int(45))
        # self.input_clipY.setText(str(window.clipY))
        self.q_clipX = MyQTextEdit('Clip X', window.clipX, self.gridlayout, 8)
        self.q_clipY = MyQTextEdit('Clip Y', window.clipY, self.gridlayout, 9)
        # self.ui.slider_clipZ.setValue(int(self.slider_clipZ))

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

        # Use constants instead of explicit definition
        self.clipX = 45
        self.clipY = 315
        self.clipZ = 0

    def set_callback(self):
        self.ui.push_screenshot.clicked.connect(self.screenshot_callback)
        self.ui.push_camera.clicked.connect(self.camera_callback)
        self.ui.push_quit.clicked.connect(self.quit_callback)
        self.ui.push_start.clicked.connect(self.start_callback)
        self.ui.push_reset.clicked.connect(self.reset_camera)

        self.ui.q_clipX.set_callback(self.clipX_callback)
        self.ui.q_clipY.set_callback(self.clipY_callback)

        # self.iren.AddObserver("TimerEvent", sync_cameras)
        # timer_id = interactor.CreateRepeatingTimer(10) 

    def run(self):
        self.show()
        self.setWindowState(Qt.WindowMaximized)  # Maximize the window
        self.iren.Initialize() # Need this line to actually show
                                # the render inside Qt

    def screenshot_callback(self):
        self.save_frame()

    def camera_callback(self):
        self._print_camera_settings()

    def reset_camera(self):
        camera = self.ren.GetActiveCamera()
        camera.SetPosition(self.radius, self.radius, 6*self.radius)  # Example position
        camera.SetFocalPoint(self.radius, self.radius, self.radius)  # Example focal point
        camera.SetViewUp(0, 1, 0)  # Example view up vector
        self.ren.SetActiveCamera(camera)
        self.Update()

    def start_callback(self):
        self.time_idx = 0
        max_time_idx = len(self.voxelizer.data_list) - 1
        time_interval_ms = 1000  # Time interval in milliseconds

        # Define a function to update the scene with a sphere of increasing radius
        def update_scene(obj, event):
            if self.time_idx < max_time_idx:
                # Create a sphere source
                self.time_idx = self.time_idx + 1
                self.update_clipper()
                self.Update()
        
        # Set up the timer to trigger updates at regular intervals
        self.iren.AddObserver('TimerEvent', update_scene)
        timer_id = self.iren.CreateRepeatingTimer(time_interval_ms)  

    def clipX_callback(self, val):
        self.clipX = self.ui.q_clipX.Update()
        self.update_clipper()
        self.ui.log.insertPlainText('clipTheta1 set to {}\n'.format(self.clipX))
        self.Update()

    def clipY_callback(self):
        self.clipY = self.ui.q_clipY.Update()
        self.update_clipper()
        self.ui.log.insertPlainText('clipTheta2 set to {}\n'.format(self.clipY))
        self.Update()

    # def clipZ_callback(self, val):
    #     self.clipZ = val
    #     self.update_clipper()
    #     self.ui.log.insertPlainText('clipZ set to {}\n'.format(self.clipZ))
    #     self.Update()

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
        log_html = [
            f"<li><div style='font-weight:bold'>Position:</div> {camera.GetPosition()}</li>",
            f"<li><div style='font-weight:bold'>Focal point:</div> {camera.GetFocalPoint()}</li>",
            f"<li><div style='font-weight:bold'>View up:</div> {camera.GetViewUp()}</li>",
            f"<li><div style='font-weight:bold'>View right:</div> {GetViewRight(camera)}</li>",
            f"<li><div style='font-weight:bold'>Clipping range:</div> {camera.GetClippingRange()}</li>",
        ]
        log_html = ''.join(log_html)
        text_window.setHtml(
            f"<div style='font-weight:bold'>Camera settings:</div><p><ul>{log_html}</ul>")
        log.insertPlainText('Updated camera info\n')

        camera_filename = self.output + '_camera.json'
        vtk_camera.save_camera(camera, filename=camera_filename)
        log.insertPlainText(f'Saved camera settings to {camera_filename}\n')

    def load_camera(self, camera=None):
        if camera is not None:
            self.ren.SetActiveCamera(vtk_camera.load_camera(camera))

    def Update(self):
        self.ui.vtkWidget.GetRenderWindow().Render()

        # Windows has a bug where the renderer doesn't update scalar data on the GPU.
        # This artificially causes a timestamp update which causes that update.
        # https://discourse.vtk.org/t/correct-way-to-update-a-vtkimagedata-and-refresh-the-render-window-renderwindow-render-not-working/6359/13
        self.ui.vtkWidget.GetRenderWindow().GetInteractor().ProcessEvents()
