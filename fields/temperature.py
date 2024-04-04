import vtk
from PyQt5.QtWidgets import QSlider, QLabel

from .base import UiBase, PyQtBase
from .vtk_helper.vtk_io_helper import readVTK
from .cmap import TransferFunction
from vtk.util import numpy_support
import numpy as np
from .utils import voxelize, get_poly_data, ScalarField

class PyQtTemperature(PyQtBase):

    def __init__(self, 
        data,
        output='temperature'
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
            title="Temperature"
        ) 

        # vtk_poly_data = get_poly_data(data[0], 'temperature')

        vtk_image_data = voxelize(data[0], 'temperature', resolution=100)

        self.field_temperature = ScalarField(vtk_image_data, self.tf)

        # isosurface = Isosurface(
        #     vtk_poly_data, 2000, (1.0, 0.0, 0.0), 1.0)

        # Create the Renderer
        self.ren = vtk.vtkRenderer()
        self.ren.AddVolume(self.field_temperature.volume)
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