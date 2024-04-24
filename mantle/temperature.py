import vtk
from .cmap import TransferFunction
from .scalar import PyQtScalar

class PyQtTemperature(PyQtScalar):

    def __init__(self, 
        data,
        resolution = 100,
    ):
        attr = 'temperature'
        name = 'temperature'
        tf = TransferFunction(
            ctf_tuples=[
                [0, 0.0, 1.0, 0.0],
                [1801, 0.0, 0.0, 1.0],
                [2350, 1.0, 1.0, 1.0],
                [2700, 1.0, 0.0, 0.0],
                [2801, 1.0, 1.0, 0.0]
            ],
            otf_tuples=[
                [0, 0.0],
                [300, 0.1],
            ],
            title=name.title()
        )
        super().__init__(data, attr, name, tf, resolution=resolution)
        
        