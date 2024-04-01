import vtk
from PyQt5.QtWidgets import QSlider
from PyQt5.QtCore import Qt

from .vtk_helper.vtk_io_helper import readVTK
import numpy as np
from vtk.util import numpy_support

def get_poly_data(nc_data, attr='temperature'):
    xx, yy, zz = np.meshgrid(
        np.radians(nc_data.lon), 
        np.radians(nc_data.lat), 
        nc_data.r
    )
    
    data = np.array(getattr(nc_data, attr))

    vtk_data = numpy_support.numpy_to_vtk(
            num_array=data.ravel(), 
            deep=True, array_type=vtk.VTK_FLOAT)
        
    X = zz * np.cos(yy) * np.cos(xx)
    Y = zz * np.cos(yy) * np.sin(xx) 
    Z = zz * np.sin(yy)
    points = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1)
    # Create a vtkPoints object and set the points from the NumPy array
    vtk_points = vtk.vtkPoints()
    vtk_points.SetData(numpy_support.numpy_to_vtk(points, deep=True))

    vtk_poly_data = vtk.vtkPolyData()
    vtk_poly_data.SetPoints(vtk_points)
    vtk_poly_data.GetPointData().SetScalars(vtk_data)
    
    return vtk_poly_data

def xyz2lonlatr(x, y, z, eps=1e-12):
    r = np.sqrt(x**2 + y**2 + z**2)
    lat = np.arccos(z / (r+eps)) * 180 / np.pi
    lon = np.arctan(y / (x+eps)) * 180 / np.pi
    return lon, lat, r

def lonlatr2xyz(lon, lat, r):
    lon = np.radians(lon)
    lat = np.radians(lat)
    x = r * np.cos(lat) * np.cos(lon)
    y = r * np.cos(lat) * np.sin(lon) 
    z = r * np.sin(lat)
    return x, y, z

import bisect
def voxelize(nc_data, attr, r1=3000, r2=6000, lon1=0, lon2=90, resolution=10, eps=1e-6):
    rmax = int(nc_data.r[-1])
    image_data = np.zeros([2*rmax, 2*rmax, 2*rmax])
    data = getattr(nc_data, attr)
    for i, lat in enumerate(np.array(nc_data.lat)):
        print(i, lat)
        for j, lon in enumerate(np.array(nc_data.lon)):
            for r in [r1, r2]:
                k = bisect.bisect_left(nc_data.r, r)
                x, y, z = lonlatr2xyz(lon, lat, r)
                # print(x, y, z, lon, lat, r, i, j, k)
                x = int(x + rmax)
                y = int(y + rmax)
                z = int(z + rmax)
                value = data[i, k, j]
                image_data[x, y, z] = value
            
    
    
    
    
    # rmax = nc_data.r[-1]

    
    # X = np.linspace(-rmax+eps, rmax-eps, resolution)
    # Y = np.linspace(-rmax+eps, rmax-eps, resolution)
    # Z = np.linspace(-rmax+eps, rmax-eps, resolution)
    # meshgrid = np.meshgrid(X, Y, Z)
    # print(meshgrid.shape)
    # raise

    # for i, x in enumerate(np.linspace(-rmax+eps, rmax-eps, resolution)):
    #     print(i)
    #     for j, y in enumerate(np.linspace(-rmax+eps, rmax-eps, resolution)):
    #         for k, z in enumerate(np.linspace(-rmax+eps, rmax-eps, resolution)):
    #             lon, lat, r = xyz2lonlatr(x, y, z)
    #             r_id = bisect.bisect_right(data.r, r)
    #             if r_id == len(data.r) - 1:
    #                 lon_id = bisect.bisect_right(data.lon, lon)
    #                 lat_id = bisect.bisect_right(data.lat, lat)
                    
    #                 # print(lon, r, lat)
    #                 # print(lon_id, r_id, lat_id)
    #                 image_data[i, j, k] = data.temperature[lon_id, r_id, lat_id]

    vtk_image_data = vtk.vtkImageData()
    vtk_image_data.SetDimensions(resolution, resolution, resolution)
    vtk_data = numpy_support.numpy_to_vtk(
            num_array=image_data.ravel(), 
            deep=True, array_type=vtk.VTK_FLOAT)
    vtk_image_data.GetPointData().SetScalars(vtk_data)

    return vtk_image_data


class Data:

    def __init__(self, filename):
        self.reader = readVTK(filename)
        self.reader.Update()
    
        self.mapper = vtk.vtkDataSetMapper()
        self.mapper.SetInputConnection(self.reader.GetOutputPort())
        self.mapper.ScalarVisibilityOn()

        self.actor = vtk.vtkActor()
        self.actor.SetMapper(self.mapper)

# Setting up widgets
def slider_setup(slider, val, bounds, interv):
    slider.setOrientation(Qt.Horizontal)
    slider.setValue(int(val))
    slider.setTracking(False)
    slider.setTickInterval(interv)
    slider.setTickPosition(QSlider.TicksAbove)
    slider.setRange(bounds[0], bounds[1])
