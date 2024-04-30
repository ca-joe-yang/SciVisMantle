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
from .cmap import get_tf, TransferFunction
from .velocity_field import Glyph

class PyQtScalar(PyQtBase):

    def __init__(self, 
        data_dir, resolution, version
    ):
        super().__init__(resolution)
        self.ui = UiBase()
        self.ui.setupUi(self)

        self.attr_l = 'temperature'
        self.attr_r = 'temperature'

        self.resolution = resolution
        self.radius = int(resolution/2)
        self.center = (self.radius, self.radius, self.radius)
        self.borders = ClipBorders(self.clipX, self.clipY, self.radius)

        self.voxelizer = Voxelizer(data_dir, self.resolution)
        self.voxelizer.check_all()
        self.vtk_image_data_l = vtk.vtkImageData()
        self.vtk_image_data_l.SetDimensions(self.resolution, self.resolution, self.resolution)
        self.tf_l = TransferFunction(self.attr_l, 'left')
        self.field_l = ScalarField(self.vtk_image_data_l, self.tf_l)

        self.vtk_image_data_r = vtk.vtkImageData()
        self.vtk_image_data_r.SetDimensions(self.resolution, self.resolution, self.resolution)
        self.tf_r = TransferFunction(self.attr_r, 'right')
        self.field_r = ScalarField(self.vtk_image_data_r, self.tf_r)

        self.vx_image_data = vtk.vtkImageData()
        self.vx_image_data.SetDimensions(self.resolution, self.resolution, self.resolution)

        self.vy_image_data = vtk.vtkImageData()
        self.vy_image_data.SetDimensions(self.resolution, self.resolution, self.resolution)

        self.vz_image_data = vtk.vtkImageData()
        self.vz_image_data.SetDimensions(self.resolution, self.resolution, self.resolution)

        self.vector_field = vtk.vtkImageData()
        self.num_points = self.vx_image_data.GetNumberOfPoints()

        self.vectors = vtk.vtkFloatArray()
        self.vectors.SetNumberOfComponents(3)
        self.vectors.SetNumberOfTuples(self.num_points)

        self.color_mode = 'magnitude'
        self.tf_v = TransferFunction('magnitude', 'right')
        self.glyph3d = Glyph(self.vector_field, self.color_mode, self.tf_v)
        

        self.resolution = resolution

        # Create the Renderer
        self.ren = vtk.vtkRenderer()
        self.reset_camera()

        self.version = version

        if version == 'ss':
            self.velocity_mode = 'right'
        elif version == 'sv':
            self.velocity_mode = 'right'
        else:
            self.velocity_mode = None

        self.update_clipper()
        if version == 'ss':
            self.velocity_mode = 'right'
            self.ren.AddVolume(self.field_l.volume)
            self.ren.AddVolume(self.field_r.volume)
            self.ren.AddActor2D(self.tf_l.bar.get())    
            self.ren.AddActor2D(self.tf_r.bar.get())
        elif version == 'sv':
            self.velocity_mode = 'right'
            self.ren.AddVolume(self.field_l.volume)
            self.ren.AddActor2D(self.tf_l.bar.get())    
            self.ren.AddActor(self.glyph3d.actor)
            self.ren.AddActor2D(self.tf_v.bar.get())
        else:
            self.velocity_mode = None
            self.ren.AddActor(self.glyph3d.actor)
            self.ren.AddActor2D(self.tf_v.bar.get())
        for actor in self.borders.actors:
            self.ren.AddActor(actor)
        self.ren.AddActor(self.sphere.actor)
        for actor in self.borders.actors:
            self.ren.AddActor(actor)
        for location in self.locations:
            self.ren.AddActor(location.actor)
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
        camera = self.ren.GetActiveCamera()
        vtk_data_l = self.voxelizer.Update(
            self.time_idx, self.attr_l,
            camera, 'left'
        )
        self.vtk_image_data_l.GetPointData().SetScalars(vtk_data_l)
        self.field_l.Update(self.vtk_image_data_l)

        vtk_data_r = self.voxelizer.Update(
            self.time_idx, self.attr_r,
            camera, 'right'
        )
        self.vtk_image_data_r.GetPointData().SetScalars(vtk_data_r)
        self.field_r.Update(self.vtk_image_data_r)

        if self.version != 'ss':
            vtk_data_vx = self.voxelizer.Update(
                self.time_idx, 'vx',
                camera, self.velocity_mode
            )
            self.vx_image_data.GetPointData().SetScalars(vtk_data_vx)

            vtk_data_vy = self.voxelizer.Update(
                self.time_idx, 'vy',
                camera, self.velocity_mode
            )
            self.vy_image_data.GetPointData().SetScalars(vtk_data_vy)

            vtk_data_vz = self.voxelizer.Update(
                self.time_idx, 'vz',
                camera, self.velocity_mode
            )
            self.vz_image_data.GetPointData().SetScalars(vtk_data_vz)

            # TODO:
            # All of this below is just repeated code from before. 
            # It's late and I don't want to make a better solution for now right before
            # presentations, so here we go.
            self.vector_field.DeepCopy(self.vx_image_data) 
            self.vector_field.GetPointData().SetScalars(self.vx_image_data.GetPointData().GetScalars())
            self.vector_field.GetPointData().AddArray(self.vy_image_data.GetPointData().GetScalars())
            self.vector_field.GetPointData().AddArray(self.vz_image_data.GetPointData().GetScalars())

            for i in range(self.num_points):
                x = self.vx_image_data.GetPointData().GetScalars().GetValue(i)
                y = self.vy_image_data.GetPointData().GetScalars().GetValue(i)
                z = self.vz_image_data.GetPointData().GetScalars().GetValue(i)
                self.vectors.SetTuple3(i, x, y, z)

            self.vector_field.GetPointData().SetVectors(self.vectors)

    def update_clipper(self):
        self.voxelizer.build_clip_mask(self.clipX, self.clipY)
        self.borders.Update(self.clipX, self.clipY)
        self.UpdateData()
        
