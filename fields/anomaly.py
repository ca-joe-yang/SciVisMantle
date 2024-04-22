import vtk
from PyQt5.QtWidgets import QSlider, QLabel

from .base import UiBase, PyQtBase
from .vtk_helper.vtk_io_helper import readVTK
from .cmap import TransferFunction
from vtk.util import numpy_support
import numpy as np
from .utils import voxelize, ScalarField

class PyQtAnomaly(PyQtBase):

    def __init__(self, 
        data,
        output='anomaly',
        resolution = 100
    ):
        super().__init__(output)
        self.ui = UiBase()
        self.ui.setupUi(self)

        # temperature = np.array(data[0].temperature)
        self.tf = TransferFunction(
            ctf_tuples=[
                [-500, 0.0, 0.0, 1.0],
                [0, 1.0, 1.0, 1.0],
                [500, 1.0, 0.0, 0.0]
            ],
            otf_tuples=[
                [-10000, 0.0],
                [-100, 0.1],
                [0, 0.0001],
                [100, 0.1],
                # [1000, 0.1],
            ],
            title="anomaly"
        ) 

        self.data = data[0]
        self.resolution = resolution

        vtk_image_data = voxelize(self.data, 'temperature anomaly', resolution=self.resolution)

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

    def update_clipper(self):
        vtk_image_data = voxelize(self.data, 'temperature anomaly', resolution=self.resolution, 
                                       clip_theta1=self.clipX, clip_theta2=self.clipY)

        self.ren.RemoveVolume(self.field.volume)

        self.field = ScalarField(vtk_image_data, self.tf)

        self.ren.AddVolume(self.field.volume)