#!/usr/bin/env python

# Purdue CS530 - Introduction to Scientific Visualization
# Spring 2024
import sys
import argparse

from PyQt5.QtWidgets import QApplication

from mantle import PyQtScalar, PyQtVelocity

from mantle.data import load_data
    
if __name__=="__main__":
    # -d[--data] <DATA_DIRECTORY>
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", type=str, default='data',
                        help="the directory to all sphericalxxx.nc")
    parser.add_argument("-f", "--field", type=str, choices=["temperature", "conductivity", "anomaly", 
                                                            "expansivity", "velocity"], default="temperature", 
                                                            help = "Which field to visualize (default: temperature)")
    parser.add_argument("-r", "--resolution", type=int, default=100, help="Resolution of dataset voxelization")
    parser.add_argument("--color_by_vector", action='store_true', default=False, 
                        help="Colors velocity glyphs by vector orientation instead of by magnitude.")
    parser.add_argument("-v", "--version", type=str, default='ss',
                        help="mode")
    parser.add_argument("--camera", type=str, default='camera.json',
                        help="camera json")
    args = parser.parse_args()
    app = QApplication(sys.argv)
    # data = load_data(args.data)[:20]

    if args.resolution < 1:
        raise argparse.ArgumentTypeError('Resolution must be at least 1!')
    
    # if args.field == "velocity":
    #     window = PyQtVelocity(args.data, resolution=args.resolution)
    # else:
    window = PyQtScalar(args.data, resolution=args.resolution, version=args.version)
    # # window.load_camera(args.camera)
    window.run()
    sys.exit(app.exec_())
