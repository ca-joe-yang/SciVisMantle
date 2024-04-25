import vtk
from PyQt5.QtWidgets import QSlider, QLabel

from .base import UiBase, PyQtBase
from .vtk_helper.vtk_io_helper import readVTK
from .cmap import TransferFunction
from vtk.util import numpy_support
import numpy as np
from .utils import voxelize, ScalarField

class PyQtVelocity(PyQtBase):

    def __init__(self, 
        data,
        output='velocity',
        resolution = 100,
        color_mode = "magnitude"
    ):
        super().__init__(output)
        self.ui = UiBase()
        self.ui.setupUi(self)

        # temperature = np.array(data[0].temperature)
        self.tf = TransferFunction(
            ctf_tuples=[
                [0, 0.0, 1.0, 0.0],
                [1801, 0.0, 0.0, 1.0],
                [2350, 1.0, 1.0, 1.0],
                [2700, 1.0, 0.0, 0.0],
                [2801, 1.0, 1.0, 0.0]
            ],
            otf_tuples=[
                [0, 0.0],
                [300, 0.1],
            ],
            title="Velocity"
        ) 

        self.color_mode = color_mode
        self.resolution = resolution
        self.time_idx = 0
        self.data = data

        self.vx_image_data = voxelize(self.data[self.time_idx], 'vx', resolution=self.resolution, clip_theta1=90)
        self.vy_image_data = voxelize(self.data[self.time_idx], 'vy', resolution=self.resolution, clip_theta1=90)
        self.vz_image_data = voxelize(self.data[self.time_idx], 'vz', resolution=self.resolution, clip_theta1=90)


        vector_field = vtk.vtkImageData()
        vector_field.DeepCopy(self.vx_image_data) 
        vector_field.GetPointData().SetScalars(self.vx_image_data.GetPointData().GetScalars())
        vector_field.GetPointData().AddArray(self.vy_image_data.GetPointData().GetScalars())
        vector_field.GetPointData().AddArray(self.vz_image_data.GetPointData().GetScalars())

        num_points = self.vx_image_data.GetNumberOfPoints()

        vectors = vtk.vtkFloatArray()
        vectors.SetNumberOfComponents(3)
        vectors.SetNumberOfTuples(num_points)

        for i in range(num_points):
            x = self.vx_image_data.GetPointData().GetScalars().GetValue(i)
            y = self.vy_image_data.GetPointData().GetScalars().GetValue(i)
            z = self.vz_image_data.GetPointData().GetScalars().GetValue(i)
            vectors.SetTuple3(i, x, y, z)

        vector_field.GetPointData().SetVectors(vectors)

        # Filter out points with scalar value equal to -10000
        threshold = vtk.vtkThreshold()
        threshold.SetInputData(vector_field)
        threshold.SetLowerThreshold(-9999)  # Set threshold to filter out -10000
        threshold.Update()
        
        # Get the scalar range
        scalarRange = threshold.GetOutput().GetScalarRange()
        minScalarValue = scalarRange[0]
        maxScalarValue = scalarRange[1]

        ctf = vtk.vtkColorTransferFunction()
        # ctf.AddRGBPoint(minScalarValue, 0.001462, 0.000466, 0.013866)
        # ctf.AddRGBPoint((minScalarValue + maxScalarValue) / 2, 0.365953, 0.146965, 0.472712)
        # ctf.AddRGBPoint(maxScalarValue, 0.988362, 0.998364, 0.644924)
        ctf.AddRGBPoint(minScalarValue, 0, 0, 1)
        # ctf.AddRGBPoint((minScalarValue + maxScalarValue) / 2, 0, 1, 0)
        ctf.AddRGBPoint(maxScalarValue, 1, 0, 0)

        # Create glyphs to visualize the vector field
        # Create arrow source for glyphs
        arrow_source = vtk.vtkArrowSource()

        glyph = vtk.vtkGlyph3D()
        # Set the arrow source as the glyph source
        glyph.SetSourceConnection(arrow_source.GetOutputPort())
        glyph.SetInputConnection(threshold.GetOutputPort())
        glyph.SetScaleFactor(1e9)  # Adjust the scaling factor as needed
        if self.color_mode == "magnitude":
            glyph.SetColorModeToColorByScale()
        else:
            glyph.SetColorModeToColorByVector()
        # glyph.SetScaleFactor(1.5e-6)

        # Create mapper and actor for glyphs
        glyph_mapper = vtk.vtkPolyDataMapper()
        glyph_mapper.SetInputConnection(glyph.GetOutputPort())
        glyph_mapper.SetLookupTable(ctf)
        glyph_mapper.SetScalarRange(minScalarValue, maxScalarValue)

        self.glyph_actor = vtk.vtkActor()
        self.glyph_actor.SetMapper(glyph_mapper)

        # Create the Renderer
        self.ren = vtk.vtkRenderer()
        self.first_render = True
        # self.ren.AddVolume(self.field_temperature.volume)
        self.ren.AddActor(self.glyph_actor)
        # self.ren.AddActor(self.field_temperature.actor)
        # self.ren.AddActor(isosurface.actor)
        # self.ren.AddActor(self.axes.actor)
        # self.ren.AddActor2D(self.tf.bar.get())
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
            self.ren.RemoveActor(self.glyph_actor)

        self.vx_image_data = voxelize(
            self.data[self.time_idx], 'vx', resolution=self.resolution, 
            clip_theta1=self.clipX, clip_theta2=self.clipY)
        self.vy_image_data = voxelize(
            self.data[self.time_idx], 'vy', resolution=self.resolution, 
            clip_theta1=self.clipX, clip_theta2=self.clipY)
        self.vz_image_data = voxelize(
            self.data[self.time_idx], 'vz', resolution=self.resolution, 
            clip_theta1=self.clipX, clip_theta2=self.clipY)

        # TODO:
        # All of this below is just repeated code from before. 
        # It's late and I don't want to make a better solution for now right before
        # presentations, so here we go.

        vector_field = vtk.vtkImageData()
        vector_field.DeepCopy(self.vx_image_data) 
        vector_field.GetPointData().SetScalars(self.vx_image_data.GetPointData().GetScalars())
        vector_field.GetPointData().AddArray(self.vy_image_data.GetPointData().GetScalars())
        vector_field.GetPointData().AddArray(self.vz_image_data.GetPointData().GetScalars())

        num_points = self.vx_image_data.GetNumberOfPoints()

        vectors = vtk.vtkFloatArray()
        vectors.SetNumberOfComponents(3)
        vectors.SetNumberOfTuples(num_points)

        for i in range(num_points):
            x = self.vx_image_data.GetPointData().GetScalars().GetValue(i)
            y = self.vy_image_data.GetPointData().GetScalars().GetValue(i)
            z = self.vz_image_data.GetPointData().GetScalars().GetValue(i)
            vectors.SetTuple3(i, x, y, z)

        vector_field.GetPointData().SetVectors(vectors)

        # Filter out points with scalar value equal to -10000
        threshold = vtk.vtkThreshold()
        threshold.SetInputData(vector_field)
        threshold.SetLowerThreshold(-9999)  # Set threshold to filter out -10000
        threshold.Update()
        
        # Get the scalar range
        scalarRange = threshold.GetOutput().GetScalarRange()
        minScalarValue = scalarRange[0]
        maxScalarValue = scalarRange[1]

        ctf = vtk.vtkColorTransferFunction()
        ctf.AddRGBPoint(minScalarValue, 0.001462, 0.000466, 0.013866)
        ctf.AddRGBPoint((minScalarValue + maxScalarValue) / 2, 0.365953, 0.146965, 0.472712)
        ctf.AddRGBPoint(maxScalarValue, 0.988362, 0.998364, 0.644924)

        # Create glyphs to visualize the vector field
        # Create arrow source for glyphs
        arrow_source = vtk.vtkArrowSource()

        glyph = vtk.vtkGlyph3D()
        # Set the arrow source as the glyph source
        glyph.SetSourceConnection(arrow_source.GetOutputPort())
        glyph.SetInputConnection(threshold.GetOutputPort())
        glyph.SetScaleFactor(1e9)  # Adjust the scaling factor as needed
        if self.color_mode == "magnitude":
            glyph.SetColorModeToColorByScale()
        else:
            glyph.SetColorModeToColorByVector()
        # glyph.SetScaleFactor(1.5e-6)

        # Create mapper and actor for glyphs
        glyph_mapper = vtk.vtkPolyDataMapper()
        glyph_mapper.SetInputConnection(glyph.GetOutputPort())
        glyph_mapper.SetLookupTable(ctf)
        glyph_mapper.SetScalarRange(minScalarValue, maxScalarValue)

        self.glyph_actor = vtk.vtkActor()
        self.glyph_actor.SetMapper(glyph_mapper)
        
        self.ren.AddActor(self.glyph_actor)