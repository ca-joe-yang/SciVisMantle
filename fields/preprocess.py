import vtk
import numpy as np

import xarray as xr
import os
def load_data(data_dir, num=None):
    data_paths = [ os.path.join(data_dir, f) for f in os.listdir(data_dir) \
        if f.endswith('.nc') and f.startswith('spherical') ]
    if num is not None:
        data_paths = data_paths[:num]
    data = [ xr.open_dataset(path) for path in data_paths ]
    return data

def xyz2lonlatr(x, y, z, eps=1e-12):
    r = np.sqrt(x**2 + y**2 + z**2)
    lat = np.arccos(z / (r+eps)) * 180 / np.pi
    lat[lat > 90] = (lat - 180)[lat > 90]
    lon = np.arctan(y / (x+eps)) * 180 / np.pi
    return lon, lat, r

if __name__ == '__main__':
    nc_data = load_data('../data')[0]
    # poly_data = get_poly_data(nc_data, 'temperature')

    resolution = 10
    eps = 1e-12
    attr = 'temperature'

    rmax = int(nc_data.r[-1])
    image_data = np.zeros([resolution, resolution, resolution])
    data = getattr(nc_data, attr)

    X = np.linspace(-rmax+eps, rmax-eps, resolution)
    Y = np.linspace(-rmax+eps, rmax-eps, resolution)
    Z = np.linspace(-rmax+eps, rmax-eps, resolution)
    meshgrid = np.meshgrid(X, Y, Z)

    Lon, Lat, R = xyz2lonlatr(meshgrid[0], meshgrid[1], meshgrid[2])

    lon_ids = np.searchsorted(nc_data.lon, Lon)
    lat_ids = len(nc_data.lat) - np.searchsorted(-nc_data.lat, Lat)
    r_ids = np.searchsorted(nc_data.r, R)

    for i in range(resolution):
        print(i)
        for j in range(resolution):
            for k in range(resolution):
                print(i, j, k, lat_ids[i, j, k])
                if r_ids[i, j, k] < 201:
                    lon = lon_ids[i, j, k] 
                    lat = lat_ids[i, j, k]
                    r = r_ids[i, j, k]
                    image_data[i, j, k] = data[lon, r, lat]
    