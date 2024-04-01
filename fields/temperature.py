import vtk
from PyQt5.QtWidgets import QSlider, QLabel

from .base import UiBase, PyQtBase
from .vtk_helper.vtk_io_helper import readVTK
from .cmap import TransferFunction
from vtk.util import numpy_support
import numpy as np
from .utils import voxelize, get_poly_data
from .isosurface import Isosurface

class MySphere:

    def __init__(self):
        self.reader = readVTK('data/spherical001.nc')
        self.reader.Update()
        print(reader)

        # self.actor = vtk.vtkActor()
        # self.actor.SetMapper(mapper)

def polydata_to_image(polydata, dimensions=(10, 10, 10)):
    # Get the bounds of the polydata
    bounds = polydata.GetBounds()
    xmin, xmax, ymin, ymax, zmin, zmax = bounds

    # Create vtkImageData
    imageData = vtk.vtkImageData()
    imageData.SetDimensions(dimensions)
    imageData.SetSpacing((xmax - xmin) / (dimensions[0] - 1),
                        (ymax - ymin) / (dimensions[1] - 1),
                        (zmax - zmin) / (dimensions[2] - 1))
    imageData.SetOrigin(xmin, ymin, zmin)
    imageData.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)

    # Initialize all voxels to 0
    print(imageData.GetNumberOfPoints())
    for i in range(imageData.GetNumberOfPoints()):
        imageData.GetPointData().GetScalars().SetTuple1(i, -1)

    # Iterate over all cells in the polydata
    # for cellId in range(polydata.GetNumberOfCells()):
        # print(cellId)
        # cell = polydata.GetCell(cellId)
        # bounds = cell.GetBounds()
    xmin, xmax, ymin, ymax, zmin, zmax = bounds

    # Iterate over all points in the cell
    for i, x in enumerate(np.linspace(xmin, xmax, dimensions[0])):
        for j, y in enumerate(np.linspace(ymin, ymax, dimensions[1])):
            for k, z in enumerate(np.linspace(zmin, zmax, dimensions[2])):
                # print(i, j, k)
                # Check if the point (i,j,k) is inside the cell
                if x**2 + y**2 + z**2 <= 100000:
                    # Convert (i,j,k) to index in vtkImageData
                    index = imageData.ComputePointId([i, j, k])
                    print(index, i, j, k)
                    # Set the voxel value to 255 (or any desired value)
                    imageData.GetPointData().GetScalars().SetTuple1(index, 3000)

    return imageData

class FieldTemperature:

    def __init__(self, data, tf):
        self.property = vtk.vtkVolumeProperty()
        self.property.ShadeOff()
        self.property.SetColor(tf.ctf)
        self.property.SetScalarOpacity(tf.otf)
        self.property.SetInterpolationTypeToLinear()

        self.mapper = vtk.vtkSmartVolumeMapper()
        self.mapper.SetInputData(data)
        self.mapper.SetBlendModeToComposite()

        self.volume = vtk.vtkVolume()
        self.volume.SetMapper(self.mapper)
        self.volume.SetProperty(self.property)

        # self.mapper = vtk.vtkPolyDataMapper()
        # self.mapper.SetInputData(data)
        # self.mapper.ScalarVisibilityOn()
        # self.mapper.SetLookupTable(tf.ctf) 
        # self.mapper.UseLookupTableScalarRangeOn()

        # self.actor = vtk.vtkActor()
        # self.actor.SetMapper(self.mapper)
        # self.actor.GetProperty().SetOpacity(0.5)

class PyQtTemperature(PyQtBase):

    def __init__(self, 
        data,
        output='temperature'
    ):
        super().__init__(output)
        self.ui = UiBase()
        self.ui.setupUi(self)

        temperature = np.array(data[0].temperature)
        data_min = np.min(temperature)
        data_max = np.max(temperature)
        data_med = (data_min + data_max) / 2
        

        self.tf = TransferFunction(
            ctf_tuples=[
                [data_min, 0.0, 0.0, 1.0],
                [data_med, 1.0, 1.0, 1.0],
                [data_max, 1.0, 0.0, 0.0]
            ],
            otf_tuples=[
                [0, 0.0],
                [data_min, 0.2],
                [data_med, 0.2],
                [data_max, 0.2]
            ],
            title="Temperature"
        ) 

        # vtk_poly_data = get_poly_data(data[0], 'temperature')

        vtk_image_data = voxelize(data[0], 'temperature')

        self.field_temperature = FieldTemperature(vtk_image_data, self.tf)

        # isosurface = Isosurface(
        #     vtk_poly_data, 2000, (1.0, 0.0, 0.0), 1.0)

        # Create the Renderer
        self.ren = vtk.vtkRenderer()
        self.ren.AddVolume(self.field_temperature.volume)
        # self.ren.AddActor(self.field_temperature.actor)
        # self.ren.AddActor(isosurface.actor)
        self.ren.AddActor(self.axes.actor)
        self.ren.AddActor2D(self.tf.bar.get())
        self.ren.ResetCamera()
        self.ren.GradientBackgroundOn()  # Set gradient for background
        self.ren.SetBackground(0.0, 0.0, 0.0)  # Set background to silver
        
        self.ui.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.ui.vtkWidget.GetRenderWindow().GetInteractor()

        self.Update()
        self.set_callback()