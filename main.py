#!/usr/bin/env python

# Purdue CS530 - Introduction to Scientific Visualization
# Spring 2024
import sys
import argparse

from PyQt5.QtWidgets import QApplication

from fields import PyQtTemperature, PyQtConductivity, PyQtExpansivity, \
                   PyQtVelocity, PyQtAnomaly

import xarray as xr
import os
def load_data(data_dir, num=None):
    data_paths = [ os.path.join(data_dir, f) for f in os.listdir(data_dir) \
        if f.endswith('.nc') and f.startswith('spherical') ]
    if num is not None:
        data_paths = data_paths[:num]
    data = [ xr.open_dataset(path) for path in data_paths ]
    return data
    
if __name__=="__main__":
    # -d[--data] <DATA_DIRECTORY>
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", type=str, default='data',
                        help="the directory to all sphericalxxx.nc")
    parser.add_argument("-f", "--field", type=str, choices=["temperature", "conductivity", "anomaly", 
                                                            "expansivity", "velocity"], default="temperature", 
                                                            help = "Which field to visualize (default: temperature)")
    parser.add_argument("-r", "--resolution", type=int, default=100, help="Resolution of dataset voxelization")
    parser.add_argument("--camera", type=str, default='camera.json',
                        help="camera json")
    args = parser.parse_args()
    app = QApplication(sys.argv)
    data = load_data(args.data)
    print(len(data))

    if args.resolution < 1:
        raise argparse.ArgumentTypeError('Resolution must be at least 1!')
    
    if args.field == "temperature":
        window = PyQtTemperature(data, resolution=args.resolution)
    elif args.field == "conductivity":
        window = PyQtConductivity(data, resolution=args.resolution)
    elif args.field == "anomaly":
        window = PyQtAnomaly(data, resolution=args.resolution)
    elif args.field == "expansivity":
        window = PyQtExpansivity(data, resolution=args.resolution)
    elif args.field == "velocity":
        window = PyQtVelocity(data, resolution=args.resolution)
    else:
        raise argparse.ArgumentTypeError('Field has to be temperature, conductivity, anomaly, expansivity, or velocity!')
    # window.load_camera(args.camera)
    window.run()
    sys.exit(app.exec_())
