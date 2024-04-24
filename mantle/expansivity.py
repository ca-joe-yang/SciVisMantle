import vtk
from .cmap import TransferFunction
from .scalar import PyQtScalar

class PyQtExpansivity(PyQtScalar):

    def __init__(self, 
        data,
        resolution = 100,
    ):
        attr = 'thermal expansivity'
        name = 'expansivity'
        tf = TransferFunction(
            ctf_tuples=[
                [-4e-8, 0.0, 0.0, 1.0],
                [1e-7, 1.0, 1.0, 1.0],
                [8e-7, 1.0, 0.0, 0.0]
            ],
            otf_tuples=[
                [-2, 0.0],
                [-1, 0.1],
                # [0, 0.1],
                [1, 0.1],
                # [1000, 0.1],
            ],
            title=name.title()
        )
        super().__init__(data, attr, name, tf, resolution=resolution)
        
        