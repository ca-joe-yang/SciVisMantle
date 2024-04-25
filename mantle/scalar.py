import vtk
# from PyQt5.QtWidgets import QSlider, QLabel

from .base import UiBase, PyQtBase
# from .vtk_helper.vtk_io_helper import readVTK
# from .cmap import TransferFunction
# from vtk.util import numpy_support
# import numpy as np
from .arc import ClipBorders
from .utils import ScalarField
from .data import Voxelizer
from .cmap import get_cmap

class PyQtScalar(PyQtBase):

    def __init__(self, 
        data_dir, attr, name, tf, resolution
    ):
        super().__init__(name)
        self.ui = UiBase()
        self.ui.setupUi(self)

        self.attr_l = 'temperature'
        self.attr_r = 'temperature anomaly'

        self.resolution = resolution
        self.radius = int(resolution/2)
        self.center = (self.radius, self.radius, self.radius)
        self.borders = ClipBorders(self.clipX, self.clipY, self.radius)

        self.voxelizer = Voxelizer(data_dir, self.resolution)
        self.voxelizer.check_all()
        self.vtk_image_data_l = vtk.vtkImageData()
        self.vtk_image_data_l.SetDimensions(self.resolution, self.resolution, self.resolution)
        self.tf_l = get_cmap(self.attr_l)
        self.tf_l.SetMode('left')
        self.field_l = ScalarField(self.vtk_image_data_l, self.tf_l)

        self.vtk_image_data_r = vtk.vtkImageData()
        self.vtk_image_data_r.SetDimensions(self.resolution, self.resolution, self.resolution)
        self.tf_r = get_cmap(self.attr_r)
        self.field_r = ScalarField(self.vtk_image_data_r, self.tf_r)

        self.time_idx = 0

        self.resolution = resolution
        self.attr = attr
        self.tf = tf

        # Create the Renderer
        self.ren = vtk.vtkRenderer()
        self.reset_camera()

        self.borders = ClipBorders(self.clipX, self.clipY, self.radius)

        self.update_clipper()
        self.ren.AddVolume(self.field_l.volume)
        self.ren.AddVolume(self.field_r.volume)
        self.ren.AddActor2D(self.tf_l.bar.get())
        self.ren.AddActor2D(self.tf_r.bar.get())
        for actor in self.borders.actors:
            self.ren.AddActor(actor)
        # self.ren.AddActor(self.axes.actor)
        self.ren.GradientBackgroundOn()  # Set gradient for background
        self.ren.SetBackground(0.0, 0.0, 0.0)  # Set background to silver

        def camera_update(obj, event):
            self.UpdateData()

        self.ren.GetActiveCamera().AddObserver(
            vtk.vtkCommand.ModifiedEvent, camera_update)

        self.ui.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.ui.vtkWidget.GetRenderWindow().GetInteractor()

        self.Update()
        self.set_callback()

    def UpdateData(self):
        vtk_data_l = self.voxelizer.Update(
                self.time_idx, self.attr_l,
                self.ren.GetActiveCamera(), 'left'
            )
        self.vtk_image_data_l.GetPointData().SetScalars(vtk_data_l)
        self.field_l.Update(self.vtk_image_data_l)

        vtk_data_r = self.voxelizer.Update(
            self.time_idx, self.attr_r,
            self.ren.GetActiveCamera(), 'right'
        )
        self.vtk_image_data_r.GetPointData().SetScalars(vtk_data_r)
        self.field_r.Update(self.vtk_image_data_r)

    def update_clipper(self):
        self.voxelizer.build_clip_mask(self.clipX, self.clipY)
        self.borders.Update(self.clipX, self.clipY)
        self.UpdateData()
        
