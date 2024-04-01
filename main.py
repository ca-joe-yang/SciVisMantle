#!/usr/bin/env python

# Purdue CS530 - Introduction to Scientific Visualization
# Spring 2024
import sys
import argparse

from PyQt5.QtWidgets import QApplication

from fields import PyQtTemperature

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
    # parser.add_argument("--camera", type=str,
    #                     help="camera json")
    args = parser.parse_args()
    app = QApplication(sys.argv)
    data = load_data(args.data)

    window = PyQtTemperature(data)
    # window.load_camera(args.camera)
    window.run()
    sys.exit(app.exec_())
