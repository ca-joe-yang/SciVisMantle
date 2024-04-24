import vtk
from .vtk_helper import vtk_colorbar

class TransferFunction:

    def __init__(self, 
        ctf_tuples, otf_tuples, 
        title="Title", position=(0.8, 0.5)):
        
        # Source
        self.ctf = vtk.vtkColorTransferFunction()
        for ctf_tuple in ctf_tuples:
            self.ctf.AddRGBPoint(*ctf_tuple)

        self.otf = vtk.vtkPiecewiseFunction()
        for otf_tuple in otf_tuples:
            self.otf.AddPoint(*otf_tuple)

        self.bar = vtk_colorbar.colorbar(self.ctf)
        self.bar.set_label(nlabels=5, size=10)
        self.bar.set_position(position)
        self.bar.set_size(width=80, height=300)
        self.bar.set_title(title=title, size=10)

