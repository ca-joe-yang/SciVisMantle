import vtk
import numpy as np
from vtk.util import numpy_support

import xarray as xr
# Load NetCDF file
nc_file = "data/spherical001.nc"
nc_data = xr.open_dataset(nc_file)

# Generate sample data representing a ball
def generate_ball_data(radius, resolution):
    # Create a grid of points
    x = np.linspace(-radius, radius, resolution)
    y = np.linspace(-radius, radius, resolution)
    z = np.linspace(-radius, radius, resolution)
    xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')

    # Compute the distance from the center
    distance = np.sqrt(xx**2 + yy**2 + zz**2)

    # Create a binary mask indicating whether each point is inside the ball
    data = np.where(distance <= radius, 1, 0)

    return data

# Parameters
radius = 6000
resolution = 50

# Generate ball data
ball_data = np.array(nc_data.temperature)

# Create a vtkImageData to store the volumetric data
image_data = vtk.vtkImageData()
image_data.SetDimensions(ball_data.shape)
image_data.SetSpacing(radius * 2 / (resolution - 1),
                      radius * 2 / (resolution - 1),
                      radius * 2 / (resolution - 1))
image_data.SetOrigin(-radius, -radius, -radius)

# Convert numpy array to VTK format
vtk_data = vtk.vtkFloatArray()
vtk_data.SetNumberOfComponents(1)
vtk_data.SetNumberOfTuples(ball_data.size)
vtk_data.SetArray(
    numpy_support.numpy_to_vtk(ball_data.ravel(), deep=True, array_type=vtk.VTK_FLOAT),
    ball_data.size, 1)

# Set the scalar values to the vtkImageData
image_data.GetPointData().SetScalars(vtk_data)

# Create volume visualization
volume_mapper = vtk.vtkSmartVolumeMapper()
volume_mapper.SetInputData(image_data)

volume_property = vtk.vtkVolumeProperty()
volume_property.ShadeOn()
volume_property.SetInterpolationTypeToLinear()

otf = vtk.vtkPiecewiseFunction()
otf.AddPoint(300, 0.02)
otf.AddPoint(3700, 0.02)

ctf = vtk.vtkColorTransferFunction()
ctf.AddRGBPoint(300, 0.0, 0.0, 1.0)
ctf.AddRGBPoint(2000, 1.0, 1.0, 1.0)
ctf.AddRGBPoint(3700, 1.0, 0.0, 0.0)

volume_property.SetColor(ctf)
volume_property.SetScalarOpacity(otf)


volume = vtk.vtkVolume()
volume.SetMapper(volume_mapper)
volume.SetProperty(volume_property)

# Create renderer
renderer = vtk.vtkRenderer()
renderer.SetBackground(0.2, 0.3, 0.4)
renderer.AddVolume(volume)

# Create render window
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)

# Create render window interactor
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Start rendering
render_window.Render()
interactor.Start()