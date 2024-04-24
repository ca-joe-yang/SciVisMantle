import vtk
from .cmap import TransferFunction
from .scalar import PyQtScalar

class PyQtAnomaly(PyQtScalar):

    def __init__(self, 
        data,
        resolution = 100,
    ):
        attr = 'temperature anomaly'
        name = 'anomaly'
        tf = TransferFunction(
            ctf_tuples=[
                [-500, 0.0, 0.0, 1.0],
                [0, 1.0, 1.0, 1.0],
                [500, 1.0, 0.0, 0.0]
            ],
            otf_tuples=[
                [-10000, 0.0],
                [-100, 0.1],
                [0, 0.0001],
                [100, 0.1],
                # [1000, 0.1],
            ],
            title=name.title()
        ) 
        super().__init__(data, attr, name, tf, resolution=resolution)
        
        