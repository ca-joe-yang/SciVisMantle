import vtk
from PyQt5.QtWidgets import QSlider, QLabel

from .base import UiBase, PyQtBase
from .vtk_helper.vtk_io_helper import readVTK
from .cmap import TransferFunction
from vtk.util import numpy_support
import numpy as np
from .utils import voxelize, get_poly_data, ScalarField

class PyQtVelocity(PyQtBase):

    def __init__(self, 
        data,
        output='velocity',
        resolution = 100
    ):
        super().__init__(output)
        self.ui = UiBase()
        self.ui.setupUi(self)

        # temperature = np.array(data[0].temperature)
        # Errmmm.. Needs change
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

        self.resolution = resolution
        self.data = data[0]

        # vtk_poly_data = get_poly_data(data[0], 'temperature')

        self.vx_image_data = voxelize(self.data, 'vx', resolution=self.resolution, clip_theta1=90)
        self.vy_image_data = voxelize(self.data, 'vy', resolution=self.resolution, clip_theta1=90)
        self.vz_image_data = voxelize(self.data, 'vz', resolution=self.resolution, clip_theta1=90)


        vector_field = vtk.vtkImageData()
        vector_field.DeepCopy(self.vx_image_data) 
        vector_field.GetPointData().SetScalars(self.vx_image_data.GetPointData().GetScalars())
        vector_field.GetPointData().AddArray(self.vy_image_data.GetPointData().GetScalars())
        vector_field.GetPointData().AddArray(self.vz_image_data.GetPointData().GetScalars())

        def print_vector_field(vector_field):
            # Get dimensions of the vector field
            dims = vector_field.GetDimensions()

            # Get scalar values
            scalar_array = vector_field.GetPointData().GetScalars()

            # Loop through points and print scalar values
            for k in range(dims[2]):
                for j in range(dims[1]):
                    for i in range(dims[0]):
                        index = i + dims[0] * (j + dims[1] * k)
                        scalar_value = scalar_array.GetValue(index)
                        if scalar_value != -10000:
                            print(f"Point ({i}, {j}, {k}): Scalar Value = {scalar_value}")

        # vector field super scuff rn like only 3 dimensions with scalars??? 
        # nahhhh that shit needs to be 3 dimensions with vectors of 3 dimensions


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
        
        # Create glyphs to visualize the vector field
        # Create arrow source for glyphs
        arrow_source = vtk.vtkArrowSource()

        glyph = vtk.vtkGlyph3D()
        # Set the arrow source as the glyph source
        glyph.SetSourceConnection(arrow_source.GetOutputPort())
        glyph.SetInputConnection(threshold.GetOutputPort())
        glyph.SetVectorModeToUseVector()
        # glyph.SetScaleModeToScaleByScalar()
        # glyph.OrientOn()
        glyph.SetColorModeToColorByVector()
        glyph.SetScaleFactor(1e9)  # Adjust the scaling factor as needed
        # glyph.SetScaleFactor(1.5e-6)




        # Create mapper and actor for glyphs
        glyph_mapper = vtk.vtkPolyDataMapper()
        glyph_mapper.SetInputConnection(glyph.GetOutputPort())

        glyph_actor = vtk.vtkActor()
        glyph_actor.SetMapper(glyph_mapper)

        

        # Create the Renderer
        self.ren = vtk.vtkRenderer()
        # self.ren.AddVolume(self.field_temperature.volume)
        self.ren.AddActor(glyph_actor)
        # self.ren.AddActor(self.field_temperature.actor)
        # self.ren.AddActor(isosurface.actor)
        # self.ren.AddActor(self.axes.actor)
        self.ren.AddActor2D(self.tf.bar.get())
        self.ren.ResetCamera()
        self.ren.GradientBackgroundOn()  # Set gradient for background
        self.ren.SetBackground(0.0, 0.0, 0.0)  # Set background to silver
        # self.ren.GetActiveCamera().SetViewUp(1.0, -1.0, -1.0)

        self.ui.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.ui.vtkWidget.GetRenderWindow().GetInteractor()

        self.Update()
        self.set_callback()

    def update_clipper(self):
        self.vtk_image_data = voxelize(self.data, 'temperature', resolution=self.resolution, 
                                       clip_theta1=self.clipX, clip_theta2=self.clipY)

        self.ren.RemoveVolume(self.field_temperature.volume)

        self.field_temperature = ScalarField(self.vtk_image_data, self.tf)

        self.ren.AddVolume(self.field_temperature.volume)