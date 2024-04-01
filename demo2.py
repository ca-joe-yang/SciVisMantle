import vtk
import numpy as np
from vtk.util import numpy_support

import xarray as xr

# Load NetCDF file
nc_file = "data/spherical001.nc"
nc_data = xr.open_dataset(nc_file)

def get_points_xyz(data):
    xx, yy, zz = np.meshgrid(
        np.radians(nc_data.lon), 
        np.radians(nc_data.lat), 
        nc_data.r)
    
    grid_x = zz * np.cos(yy) * np.cos(xx)
    grid_y = zz * np.cos(yy) * np.sin(xx) 
    grid_z = zz * np.sin(yy)
    grid = np.stack([grid_x.ravel(), grid_y.ravel(), grid_z.ravel()], 1)
    vtk_points = vtk.vtkPoints()
    vtk_points.SetData(numpy_support.numpy_to_vtk(grid, deep=True))
    return vtk_points

# Extract data variables
# lon = np.radians(nc_data.variables["lon"][:])  # Convert to radians
# lat = np.radians(nc_data.variables["lat"][:])  # Convert to radians
radius = nc_data.r
data = np.array(nc_data.temperature)

# Flatten the data
data_flat = data.ravel()

# Create vtkPoints and vtkCellArray
# points = vtk.vtkPoints()
vertices = vtk.vtkCellArray()

# Add points to vtkPoints
# for i in range(len(radius)):
#     for j in range(len(lat)):
#         for k in range(len(lon)):
#             points.InsertNextPoint(x[i, j, k], y[i, j, k], z[i, j, k])
points = get_points_xyz(nc_data)

# Create a spherical surface with vtkSphereSource
sphere_source = vtk.vtkSphereSource()
sphere_source.SetCenter(0, 0, 0)
sphere_source.SetRadius(radius[-1])  # Use the last radius value
sphere_source.SetPhiResolution(100)  # Set the resolution
sphere_source.SetThetaResolution(100)
sphere_source.Update()

# Create a vtkPolyData to store the spherical surface
surface_polydata = vtk.vtkPolyData()
# surface_polydata.DeepCopy(sphere_source.GetOutput())
surface_polydata.SetPoints(points)
print(surface_polydata.GetPoints())


# Create a scalar array to store the data values
scalar_array = vtk.vtkFloatArray()
scalar_array.SetNumberOfComponents(1)
scalar_array.SetNumberOfTuples(len(data_flat))
scalar_array.SetArray(data_flat, len(data_flat), 1)

# Set scalar data to the vtkPolyData
surface_polydata.GetPointData().SetScalars(scalar_array)

ctf = vtk.vtkColorTransferFunction()
ctf.AddRGBPoint(300, 0.0, 0.0, 1.0)
ctf.AddRGBPoint(2000, 1.0, 1.0, 1.0)
ctf.AddRGBPoint(3700, 1.0, 0.0, 0.0)

# Create a mapper and actor
mapper = vtk.vtkPolyDataMapper()
mapper.SetLookupTable(ctf)
mapper.SetInputData(surface_polydata)
mapper.SetScalarRange(np.min(data), np.max(data))  # Set the scalar range

actor = vtk.vtkActor()
actor.GetProperty().SetPointSize(10)
colors = vtk.vtkNamedColors()
actor.GetProperty().SetColor(colors.GetColor3d("Yellow"))
actor.SetMapper(mapper)

# Create a renderer, render window, and interactor
renderer = vtk.vtkRenderer()
renderer.SetBackground(0.1, 0.2, 0.4)

render_window = vtk.vtkRenderWindow()
render_window.SetSize(1600, 1600)
render_window.AddRenderer(renderer)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Add actor to renderer and start the interaction
renderer.AddActor(actor)
renderer.ResetCamera()
render_window.Render()
interactor.Start()
