import vtk
# from PyQt5.QtWidgets import QSlider, QLabel

from .base import UiBase, PyQtBase
# from .vtk_helper.vtk_io_helper import readVTK
# from .cmap import TransferFunction
# from vtk.util import numpy_support
# import numpy as np
from .arc import ClipBorders
from .utils import voxelize, ScalarField

class PyQtScalar(PyQtBase):

    def __init__(self, 
        data, attr, name, tf, resolution
    ):
        super().__init__(name)
        self.ui = UiBase()
        self.ui.setupUi(self)

        self.radius = int(resolution/2)
        self.center = (self.radius, self.radius, self.radius)

        self.borders = ClipBorders(self.clipX, self.clipY, self.radius)

        self.time_idx = 0

        self.resolution = resolution
        self.data = data
        self.attr = attr
        self.tf = tf

        # Create the Renderer
        self.ren = vtk.vtkRenderer()
        self.first_render = True
        self.update_clipper()
        self.ren.AddActor2D(tf.bar.get())
        self.ren.ResetCamera()
        self.ren.GradientBackgroundOn()  # Set gradient for background
        self.ren.SetBackground(0.0, 0.0, 0.0)  # Set background to silver
        # self.ren.GetActiveCamera().SetViewUp(1.0, -1.0, -1.0)

        self.ui.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.ui.vtkWidget.GetRenderWindow().GetInteractor()
        self.first_render = False

        self.Update()
        self.set_callback()

    def update_clipper(self):
        
        if not self.first_render:
            self.ren.RemoveVolume(self.field.volume)

        self.vtk_image_data = voxelize(
            self.data[self.time_idx], self.attr, resolution=self.resolution, 
            clip_theta1=self.clipX, clip_theta2=self.clipY)
        self.field = ScalarField(self.vtk_image_data, self.tf)
        self.ren.AddVolume(self.field.volume)
    
        if not self.first_render:
            for actor in self.borders.actors:
                self.ren.RemoveActor(actor)
        self.borders = ClipBorders(self.clipX, self.clipY, self.radius)
        for actor in self.borders.actors:
            self.ren.AddActor(actor)