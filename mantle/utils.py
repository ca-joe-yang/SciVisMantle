import vtk
from PyQt5.QtWidgets import QSlider
from PyQt5.QtCore import Qt

from .vtk_helper.vtk_io_helper import readVTK
import numpy as np
from vtk.util import numpy_support

def GetViewRight(camera):
    p = np.array(camera.GetPosition())
    f = np.array(camera.GetFocalPoint())
    v = np.array(camera.GetViewUp())

    r = np.cross(f - p, v).ravel()
    return tuple(r)
    
# def get_poly_data(nc_data, attr='temperature'):
#     xx, yy, zz = np.meshgrid(
#         np.radians(nc_data.lon), 
#         np.radians(nc_data.lat), 
#         nc_data.r
#     )
    
#     data = np.array(getattr(nc_data, attr))

#     vtk_data = numpy_support.numpy_to_vtk(
#             num_array=data.ravel(), 
#             deep=True, array_type=vtk.VTK_FLOAT)
        
#     X = zz * np.cos(yy) * np.cos(xx)
#     Y = zz * np.cos(yy) * np.sin(xx) 
#     Z = zz * np.sin(yy)
#     points = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1)
#     # Create a vtkPoints object and set the points from the NumPy array
#     vtk_points = vtk.vtkPoints()
#     vtk_points.SetData(numpy_support.numpy_to_vtk(points, deep=True))

#     vtk_poly_data = vtk.vtkPolyData()
#     vtk_poly_data.SetPoints(vtk_points)
#     vtk_poly_data.GetPointData().SetScalars(vtk_data)
    
#     return vtk_poly_data

def xyz2lonlatr(x, y, z, eps=1e-12):
    r = np.sqrt(x**2 + y**2 + z**2)
    lat = np.degrees(np.arcsin(x / r))
    lon = np.degrees(np.arctan2(z, y+eps))
    lon[lon < 0] = (360 + lon)[lon < 0]
    return lon, lat, r

def lonlatr2xyz(lon, lat, r):
    lon = np.radians(lon)
    lat = np.radians(lat)
    x = r * np.cos(lat) * np.cos(lon)
    z = r * np.cos(lat) * np.sin(lon) 
    y = r * np.sin(lat)
    return x, y, z

import bisect

class Voxelizer:

    def __init__(self, nc_data, attr, resolution=200, eps=1e-12):
        self.rmax = int(nc_data.r[-1])
        self.data = np.array(nc_data[attr])
        self.resolution = resolution

        self.X = np.linspace(-self.rmax+eps, self.rmax-eps, resolution)
        self.Y = np.linspace(-self.rmax+eps, self.rmax-eps, resolution)
        self.Z = np.linspace(-self.rmax+eps, self.rmax-eps, resolution)

        self.meshgrid = np.meshgrid(self.X, self.Y, self.Z)
        self.Lon, self.Lat, self.R = xyz2lonlatr(
            self.meshgrid[0], self.meshgrid[1], self.meshgrid[2])

        self.lon_ids = np.searchsorted(nc_data.lon, self.Lon)
        self.lat_ids = len(nc_data.lat) - np.searchsorted(-nc_data.lat, self.Lat)
        self.r_ids = np.searchsorted(nc_data.r, self.R)

        self.ids = np.stack([self.lat_ids, self.r_ids, self.lon_ids], -1)

        self.mask_sphere = self.ids[..., 1] < 200 + 1

        self.ids_flatten = self.ids[..., 0] * self.data.shape[1] * self.data.shape[2] + \
            np.clip(self.ids[..., 1], a_min=0, a_max=200) * self.data.shape[1] + \
            self.ids[..., 2]
        self.ids_flatten = self.ids_flatten.ravel()
        
        self.image_data = self.data.ravel()[self.ids_flatten]
        self.image_data[np.logical_not(self.mask_sphere.ravel())] = -10000

        self.vtk_image_data = vtk.vtkImageData()
        self.vtk_image_data.SetDimensions(resolution, resolution, resolution)

        indices = np.arange(self.resolution) + 1
        self.resolution_meshgrid = np.meshgrid(indices, indices, indices)

    def forward_camera_change(self, camera, mode='left'):
        assert mode in ['left', 'right']
        p = np.array(camera.GetPosition())
        f = np.array(camera.GetFocalPoint())
        v = np.array(camera.GetViewUp())

        a = np.cross(f - p, v)[np.newaxis, :]
        b = np.stack([
            self.resolution_meshgrid[2] - p[0],
            self.resolution_meshgrid[0] - p[1],
            self.resolution_meshgrid[1] - p[2]
        ], -1)
        # # print(b)
        b = b.reshape(-1, 3)

        M = (b @ a.T).ravel()
        if mode == 'left':
            M = M >= 0
        else:
            M = M < 0
        
        # # print(M)
        # M = M > 0
        # M = self.resolution_meshgrid[2] > f[2]
        # M = M.ravel()

        # M = (self.meshgrid[0] > p[0]).ravel()
        # print(M1.shape)
        
        self.image_data_cut = np.copy(self.image_data)
        self.image_data_cut[self.cut_M.ravel()] = -10000
        
        self.image_data_cut[M] = -10000
        
        vtk_data = numpy_support.numpy_to_vtk(
            num_array=self.image_data_cut, 
            deep=True, array_type=vtk.VTK_FLOAT)
        self.vtk_image_data.GetPointData().SetScalars(vtk_data)

        return self.vtk_image_data

    def forward_base(self, lon1=0, lon2=360):

        self.cut_M = np.logical_or(self.ids[..., 2] > lon2, self.ids[..., 2] < lon1)
        self.cut_M = np.logical_and(self.meshgrid[0] > 0, self.cut_M)

        # self.image_data_cut = np.copy(self.image_data)
        # self.image_data_cut[self.cut_M.ravel()] = -10000
        
        # vtk_data = numpy_support.numpy_to_vtk(
        #         num_array=self.image_data_cut, 
        #         deep=True, array_type=vtk.VTK_FLOAT)
        # self.vtk_image_data.GetPointData().SetScalars(vtk_data)

        # return self.vtk_image_data


# def voxelize_all_sphere(nc_data, attr, resolution=200, eps=1e-12):
#     rmax = int(nc_data.r[-1])
#     image_data = np.zeros([resolution, resolution, resolution])
#     data = np.array(nc_data[attr])

#     X = np.linspace(-rmax+eps, rmax-eps, resolution)
#     Y = np.linspace(-rmax+eps, rmax-eps, resolution)
#     Z = np.linspace(-rmax+eps, rmax-eps, resolution)
#     meshgrid = np.meshgrid(X, Y, Z)

#     Lon, Lat, R = xyz2lonlatr(meshgrid[0], meshgrid[1], meshgrid[2])

#     lon_ids = np.searchsorted(nc_data.lon, Lon)
#     lat_ids = len(nc_data.lat) - np.searchsorted(-nc_data.lat, Lat)
#     r_ids = np.searchsorted(nc_data.r, R)
    
#     ids = np.stack([lat_ids, r_ids, lon_ids], -1)
    
#     mask_ball = ids[..., 1] < 201

#     ids_flatten = ids[..., 0] * data.shape[1] * data.shape[2] + np.clip(ids[..., 1], a_min=0, a_max=200) * data.shape[1] + ids[..., 2]
#     ids_flatten = ids_flatten.ravel()
    
#     image_data = data.ravel()[ids_flatten]
#     image_data[np.logical_not(mask_ball.ravel())] = -10000

#     return image_data


def voxelize(
    nc_data, attr, resolution=200, eps=1e-12, 
    clip_theta1 = 45, clip_theta2 = 315
):
    image_data = voxelize_all_sphere(nc_data, attr, resolution, eps)
    
    M1 = np.logical_and(ids[..., 2] < clip_theta2, ids[..., 2] > clip_theta1)
    M2 = np.logical_or(meshgrid[0] < 0, M1)
    # M = np.logical_and(M1, M2)
    M = M2
    # ids_flatten = ids[..., 0] * data.shape[1] * data.shape[2] + np.clip(ids[..., 1], a_min=0, a_max=200) * data.shape[1] + ids[..., 2]
    # ids_flatten = ids_flatten.ravel()
    M_flatten = M.ravel()
    
    # image_data = data.ravel()[ids_flatten]
    
    image_data[np.logical_not(M_flatten)] = -10000

    vtk_image_data = vtk.vtkImageData()
    vtk_image_data.SetDimensions(resolution, resolution, resolution)
    vtk_data = numpy_support.numpy_to_vtk(
            num_array=image_data, 
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

class ScalarField:

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

    def Update(self, data):
        self.mapper.SetInputData(data)

if __name__ == '__main__':
    x, y, z = 10, 20, 30
    lon, lat, r = xyz2lonlatr(x, y, z)
    print(lon, lat, r)
    x, y, z = lonlatr2xyz(lon, lat, r)
    print(x, y, z)