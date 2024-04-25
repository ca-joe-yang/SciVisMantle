import vtk
from .vtk_helper import vtk_colorbar

class TransferFunction:

    def __init__(self, 
        ctf_tuples, otf_tuples, 
        title="Title"):
        
        # Source
        self.ctf = vtk.vtkColorTransferFunction()
        for ctf_tuple in ctf_tuples:
            self.ctf.AddRGBPoint(*ctf_tuple)

        self.otf = vtk.vtkPiecewiseFunction()
        for otf_tuple in otf_tuples:
            self.otf.AddPoint(*otf_tuple)

        self.bar = vtk_colorbar.colorbar(self.ctf)
        self.bar.set_label(nlabels=5, size=10)
        self.bar.set_size(width=80, height=300)
        self.bar.set_title(title=title, size=10)
        self.SetMode()

    def SetMode(self, mode='right'):
        if mode == 'right':
            self.bar.set_position((0.8, 0.5))
        elif mode == 'left':
            self.bar.set_position((0.1, 0.5))

def get_cmap(attr):
    if attr == 'temperature':
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
            title='Temperature'
        )
    elif attr == 'temperature anomaly':
        tf = TransferFunction(
            ctf_tuples=[
                [-500, 0.0, 0.0, 1.0],
                [0, 1.0, 1.0, 1.0],
                [500, 1.0, 0.0, 0.0]
            ],
            otf_tuples=[
                [-10000, 0.0],
                [-500, 0.0],
                [-100, 0.1],
                [0, 0.0001],
                [100, 0.1],
                # [1000, 0.1],
            ],
            title='Anomaly'
        ) 
    else:
        raise

    return tf

