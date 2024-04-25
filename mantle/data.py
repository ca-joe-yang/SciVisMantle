import xarray as xr
import os
import numpy as np

import vtk
from vtk.util import numpy_support

from .utils import xyz2lonlatr, lonlatr2xyz

def load_data(data_dir, num=None):
    data_paths = [ os.path.join(data_dir, f) for f in os.listdir(data_dir) \
        if f.endswith('.nc') and f.startswith('spherical') ]
    if num is not None:
        data_paths = data_paths[:num]
    data = [ xr.open_dataset(path) for path in data_paths ]
    return data

class Voxelizer:

    def __init__(self, data_dir, resolution, eps=1e-12):
        data_list = load_data(data_dir)
        self.data_dir = data_dir
        nc_data = data_list[0]
        self.rmax = int(nc_data.r[-1])
        self.resolution = resolution
        self.data_list = data_list

        self.attr_list = ['temperature', 'temperature anomaly']

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

        self.mask_sphere = self.ids[..., 1] < nc_data.dims['r']

        self.ids_flatten = self.ids[..., 0] * nc_data.dims['r'] * nc_data.dims['lon'] + \
            np.clip(self.ids[..., 1], a_min=0, a_max=nc_data.dims['r']-1) * nc_data.dims['r'] + \
            self.ids[..., 2]
        self.ids_flatten = self.ids_flatten.ravel()
        
        indices = np.arange(self.resolution) + 1
        self.resolution_meshgrid = np.meshgrid(indices, indices, indices)

    def preprocess_all(self):
        for i in range(len(self.data_list)):
            for attr in self.attr_list:
                print(attr, i)
                self.preprocess(i, attr)
        
    def preprocess(self, time_idx, attr):
        image_data = np.array(self.data_list[time_idx][attr]).ravel()[self.ids_flatten]
        image_data[np.logical_not(self.mask_sphere.ravel())] = -10000
        image_data = image_data.reshape(self.resolution, self.resolution, self.resolution)

        filename = os.path.join(self.data_dir, f'voxelize-{attr.replace(" ", "_")}-{time_idx+1:02d}-{self.resolution}')
        np.save(filename, image_data)
    
    def check_all(self):
        for attr in self.attr_list:
            for time_idx in range(len(self.data_list)):
                filename = os.path.join(self.data_dir, f'voxelize-{attr.replace(" ", "_")}-{time_idx+1:02d}-{self.resolution}.npy')
                if not os.path.exists(filename):
                    self.preprocess(time_idx, attr)
    
    def Update(self, time_idx, attr, camera=None, mode='left'):
        filename = os.path.join(self.data_dir, f'voxelize-{attr.replace(" ", "_")}-{time_idx+1:02d}-{self.resolution}.npy')
        data = np.load(filename).ravel()

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
        
        data[self.cut_M.ravel()] = -10000
        data[M] = -10000
        
        vtk_data = numpy_support.numpy_to_vtk(
            num_array=data, 
            deep=True, array_type=vtk.VTK_FLOAT)
        return vtk_data

    def build_clip_mask(self, lon1=0, lon2=360):
        self.cut_M = np.logical_or(self.ids[..., 2] > lon2, self.ids[..., 2] < lon1)
        self.cut_M = np.logical_and(self.meshgrid[0] > 0, self.cut_M)

if __name__ == '__main__':
    resolution = 100
    voxelizer = Voxelizer('data', resolution)
    voxelizer.preprocess_all()
    voxelizer.load_all()
