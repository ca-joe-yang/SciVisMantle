import vtk
from PyQt5.QtWidgets import QSlider, QLabel

from .base import UiBase, PyQtBase
from .vtk_helper.vtk_io_helper import readVTK
from .cmap import TransferFunction
from vtk.util import numpy_support
import numpy as np
from .utils import voxelize, get_poly_data, ScalarField

class PyQtExpansivity(PyQtBase):

    def __init__(self, 
        data,
        output='expansivity'
    ):
        super().__init__(output)
        self.ui = UiBase()
        self.ui.setupUi(self)

        # temperature = np.array(data[0].temperature)
        self.tf = TransferFunction(
            ctf_tuples=[
                [-4e-8, 0.0, 0.0, 1.0],
                [1e-7, 1.0, 1.0, 1.0],
                [8e-7, 1.0, 0.0, 0.0]
            ],
            otf_tuples=[
                [-2, 0.0],
                [-1, 0.1],
                # [0, 0.1],
                [1, 0.1],
                # [1000, 0.1],
            ],
            title="Expansivity"
        ) 

        vtk_image_data = voxelize(data[0], 'thermal expansivity', resolution=100)

        self.field = ScalarField(vtk_image_data, self.tf)

        # Create the Renderer
        self.ren = vtk.vtkRenderer()
        self.ren.AddVolume(self.field.volume)
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