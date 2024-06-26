import sys
import os
import vtk
from .vtk_misc_helper import connect

'''
Helper functions to import and export various VTK data formats
'''

def __read(reader_type, filename):
    reader = reader_type()
    reader.SetFileName(filename)
    return reader

def __write(writer_type, input, filename):
    writer = writer_type()
    writer.SetFileName(filename)
    connect(input, writer)
    writer.Write()

def replace_extension(filename, newext):
    return os.path.splitext(filename)[0] + newext

def readVTK(filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.vtk':
        return __read(vtk.vtkDataSetReader, filename)
    elif ext == '.vti':
        return __read(vtk.vtkXMLImageDataReader, filename)
    elif ext == '.vtu':
        return __read(vtk.vtkXMLUnstructuredGridReader, filename)
    elif ext == '.vtp':
        return __read(vtk.vtkXMLPolyDataReader, filename)
    elif ext == '.vtr':
        return __read(vtk.vtkXMLRectilinearGridReader, filename)
    elif ext == '.jpg' or ext == '.jpeg':
        return __read(vtk.vtkJPEGReader, filename)
    elif ext == '.png':
        return __read(vtk.vtkPNGReader, filename)
    elif ext == '.tif' or ext == '.tiff':
        return __read(vtk.vtkTIFFReader, filename)
    elif ext == '.nrrd' or ext == '.nhdr':
        return __read(vtk.vtkNrrdReader, filename)
    elif ext == '.nc':
        return __read(vtk.vtkNetCDFReader, filename)
    elif ext == '.csv':
        return __read(vtk.vtkDelimitedTextReader, filename)
    else:
        raise TypeError(f'Unrecognized VTK file extension {ext}')

def saveVTK(dataset, filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.vtk':
        return __write(vtk.vtkDataSetWriter, dataset, filename)
    elif ext == '.vti':
        return __write(vtk.vtkXMLImageDataWriter, dataset, filename)
    elif ext == '.vtu':
        return __write(vtk.vtkXMLUnstructuredGridWriter, dataset, filename)
    elif ext == '.vtp':
        return __write(vtk.vtkXMLPolyDataWriter, dataset, filename)
    elif ext == '.vts':
        return __write(vtk.vtkXMLStructuredGridWriter, dataset, filename)
    elif ext == '.vtr':
        return __write(vtk.vtkXMLRectilinearGridWriter, dataset, filename)
    elif ext == '.jpg' or ext == '.jpeg':
        return __write(vtk.vtkJPEGWriter, filename)
    elif ext == '.png':
        return __write(vtk.vtkPNGWriter, filename)
    elif ext == '.tif' or ext == '.tiff':
        return __write(vtk.vtkTIFFWriter, filename)
    elif ext == '.csv':
        return __write(vtk.vtkDelimitedTextWriter, filename)
    else:
        raise ValueError(f'Unrecognized VTK file extension: {ext}')

def saveVTK_XML(dataset, filename):
    if isinstance(dataset, vtk.vtkImageData):
        filename = replace_extension(filename, '.vti')
    elif isinstance(dataset, vtk.vtkUnstructuredGrid):
        filename = replace_extension(filename, '.vtu')
    elif isinstance(dataset, vtk.vtkPolyData):
        filename = replace_extension(filename, '.vtp')
    elif isinstance(dataset, vtk.vtkRectilinearGrid):
        filename = replace_extension(filename, '.vtr')
    elif isinstance(dataset, vtk.vtkStructuredGrid):
        filename = replace_extension(filename, '.vts')
    else:
        filename = replace_extension(filename, '.vtk')
        print('WARNING: Unrecognized VTK dataset type. Using Legacy format')

    print(f'filename is {filename}')
    saveVTK(dataset, filename)
