'''
Quick program to describe the Mantle Convection NetCDF file including field names.

Usage Example:
> python describe_data.py -i <file.nc>
'''

import vtk 
import argparse
import numpy as np
import vtk.util.numpy_support
import netCDF4 as nc

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="describe_data.py", description='Describes the fields of a NetCDF file')
    parser.add_argument('-i', '--input', type=str, help='Data Input', required=True)

    args = parser.parse_args()
    filename = args.input

    all = nc.Dataset(filename, 'r')
    print("------------ NetCDF4 analysis ------------")
    print(all)                                   # show all variables inside this dataset
    print(all.variables['temperature'][:,:,:])   # this is a 180x201x360 numpy array
    print(all.variables['temperature'][:,:,:].shape)
    print(all.variables['r'][:])                 # radial discretization

    print("-------------- VTK analysis  --------------")
    reader = vtk.vtkNetCDFReader()
    reader.SetFileName(filename) 
    # reader.UpdateMetaData()
    reader.SetVariableArrayStatus("temperature", 1)
    reader.Update()

    output = reader.GetOutput()

    n_arr = output.GetPointData().GetNumberOfArrays()
    print("Total Fields: {n}".format(n = n_arr))

    print("Field Names:")
    for i in range(n_arr):
        array_name = output.GetPointData().GetArrayName(i)
        print("- {name}".format(name = array_name))

    temperature_array = output.GetPointData().GetArray("temperature")
    arr = vtk.util.numpy_support.vtk_to_numpy(temperature_array)
    arr = arr.reshape((180,201,360))

    print(arr.shape)

    print(np.array_equal(arr, all.variables['temperature'][:,:,:]))


# Notes:
'''
Each field is a 180 x 201 x 360 scalar field.
                lat    r    lon

Field Names:
- temperature
- spin transition-induced density anomaly
- temperature anomaly
- thermal conductivity
- thermal expansivity
- vx
- vy
- vz


'''