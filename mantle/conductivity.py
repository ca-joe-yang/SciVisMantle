import vtk
from .cmap import TransferFunction
from .scalar import PyQtScalar

class PyQtConductivity(PyQtScalar):

    def __init__(self, 
        data,
        resolution = 100,
    ):
        attr = 'thermal conductivity'
        name = 'conductivity'
        tf = TransferFunction(
            ctf_tuples=[
                [-0.05, 0.0, 0.0, 1.0],
                [0.0, 1.0, 1.0, 1.0],
                [0.05, 1.0, 0.0, 0.0]
            ],
            otf_tuples=[
                [-2, 0.0],
                [-1, 0.01],
                # [0, 0.1],
                [1, 0.01],
                # [1000, 0.1],
            ],
            title=name.title()
        )
        super().__init__(data, attr, name, tf, resolution=resolution)
        
        