import vtk
from PyQt5.QtWidgets import QSlider, QLabel

from .base import UiBase, PyQtBase
from .vtk_helper.vtk_io_helper import readVTK
from .cmap import TransferFunction
from vtk.util import numpy_support
import numpy as np
from .utils import voxelize, ScalarField
from .data import Voxelizer, load_data
from .arc import ClipBorders

class Glyph:

    def __init__(self, inputs, color_mode, tf):
        # Filter out points with scalar value equal to -10000
        self.threshold = vtk.vtkThreshold()
        self.threshold.SetInputData(inputs)
        self.threshold.SetLowerThreshold(-9999)  # Set threshold to filter out -10000

        scalarRange = self.threshold.GetOutput().GetScalarRange()
        minScalarValue = scalarRange[0]
        maxScalarValue = scalarRange[1]

        self.glyph = vtk.vtkGlyph3D()
        self.arrow_source = vtk.vtkArrowSource()
        self.arrow_source.SetTipResolution(1)  # Adjust the tip resolution
        self.arrow_source.SetShaftResolution(1)  # Adjust the shaft resolution
        # Set the arrow source as the glyph source
        self.glyph.SetSourceConnection(self.arrow_source.GetOutputPort())
        self.glyph.SetInputConnection(self.threshold.GetOutputPort())
        self.glyph.SetScaleFactor(1e9)  # Adjust the scaling factor as needed
        if color_mode == "magnitude":
            self.glyph.SetColorModeToColorByScale()
        else:
            self.glyph.SetColorModeToColorByVector()
        # self.glyph.SetResolution(32)  # Adjust the resolution as needed

        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(self.glyph.GetOutputPort())
        self.mapper.SetLookupTable(tf.ctf)
        self.mapper.SetScalarRange(minScalarValue, maxScalarValue)

        self.actor = vtk.vtkActor()
        self.actor.SetMapper(self.mapper)

        # Create a transform to shift the actor's position
        transform = vtk.vtkTransform()
        transform.Translate(1, 1, 1)  # Shift by 20 units in the X direction

        # Apply the transform to the actor
        self.actor.SetUserTransform(transform)

class PyQtVelocity(PyQtBase):

    def __init__(self, 
        data_dir,
        resolution = 100,
        color_mode = "magnitude"
    ):
        super().__init__(resolution)
        self.ui = UiBase()
        self.ui.setupUi(self)

        self.color_mode = color_mode
        self.resolution = resolution
        self.radius = int(self.resolution/2)
        self.center = (self.radius, self.radius, self.radius)
        self.borders = ClipBorders(self.clipX, self.clipY, self.radius)

        self.voxelizer = Voxelizer(data_dir, self.resolution)
        self.voxelizer.check_all()

        self.vx_image_data = vtk.vtkImageData()
        self.vx_image_data.SetDimensions(self.resolution, self.resolution, self.resolution)

        self.vy_image_data = vtk.vtkImageData()
        self.vy_image_data.SetDimensions(self.resolution, self.resolution, self.resolution)

        self.vz_image_data = vtk.vtkImageData()
        self.vz_image_data.SetDimensions(self.resolution, self.resolution, self.resolution)

        self.vector_field = vtk.vtkImageData()
        # self.vector_field.SetDimensions(self.resolution, self.resolution, self.resolution)
        # # self.vector_field.GetPointData().SetScalars(self.vx_image_data.GetPointData().GetScalars())
        # # self.vector_field.GetPointData().AddArray(self.vy_image_data.GetPointData().GetScalars())
        # # self.vector_field.GetPointData().AddArray(self.vz_image_data.GetPointData().GetScalars())

        self.num_points = self.vx_image_data.GetNumberOfPoints()

        self.vectors = vtk.vtkFloatArray()
        self.vectors.SetNumberOfComponents(3)
        self.vectors.SetNumberOfTuples(self.num_points)

        self.tf = TransferFunction('magnitude', 'right')
        
        

        # self.field = FieldVelocity(resolution, color_mode)
        # Create the Renderer
        self.ren = vtk.vtkRenderer()
        self.update_clipper()
        self.glyph3d = Glyph(self.vector_field, self.color_mode, self.tf)
        self.ren.AddActor(self.glyph3d.actor)
        self.ren.AddActor(self.sphere.actor)
        for actor in self.borders.actors:
            self.ren.AddActor(actor)
        for location in self.locations:
            self.ren.AddActor(location.actor)
        self.ren.AddActor2D(self.tf.bar.get())
        self.ren.ResetCamera()
        self.ren.GradientBackgroundOn()  # Set gradient for background
        self.ren.SetBackground(0.0, 0.0, 0.0)  # Set background to silver

        self.ui.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.ui.vtkWidget.GetRenderWindow().GetInteractor()

        self.Update()
        self.set_callback()

    def update_clipper(self):
        self.voxelizer.build_clip_mask(self.clipX, self.clipY)
        self.borders.Update(self.clipX, self.clipY)

        # self.ren.AddActor2D(self.tf_l.bar.get())
        # self.ren.AddActor2D(self.tf_r.bar.get())

        self.UpdateData()

    def UpdateData(self):
        camera = None
        vtk_data_vx = self.voxelizer.Update(
            self.time_idx, 'vx',
            camera,
        )
        self.vx_image_data.GetPointData().SetScalars(vtk_data_vx)

        vtk_data_vy = self.voxelizer.Update(
            self.time_idx, 'vy',
            camera,
        )
        self.vy_image_data.GetPointData().SetScalars(vtk_data_vy)

        vtk_data_vz = self.voxelizer.Update(
            self.time_idx, 'vz',
            camera,
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
