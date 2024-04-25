import vtk
from .vtk_helper import vtk_colorbar

class TransferFunction:

    def __init__(self, 
        attr, mode='left'):
        
        # Source
        self.ctf = vtk.vtkColorTransferFunction()
        self.otf = vtk.vtkPiecewiseFunction()
        self.bar = vtk_colorbar.colorbar(self.ctf)
        self.Update(attr)

        
        self.bar.set_label(nlabels=5, size=10)
        self.bar.set_size(width=80, height=300)

        if mode == 'right':
            self.bar.set_position((0.8, 0.5))
        elif mode == 'left':
            self.bar.set_position((0.1, 0.5))

    def Update(self, attr):
        tf_cfg = tf_factory[attr]
        ctf_tuples = tf_cfg['ctf_tuples']
        otf_tuples = tf_cfg['otf_tuples']
        title = tf_cfg['title']

        self.ctf.RemoveAllPoints()
        for ctf_tuple in ctf_tuples:
            self.ctf.AddRGBPoint(*ctf_tuple)

        self.otf.RemoveAllPoints()
        for otf_tuple in otf_tuples:
            self.otf.AddPoint(*otf_tuple)

        self.bar.set_title(title=title, size=10)

tf_factory = {
    'temperature': {
        'ctf_tuples': [
            [0, 0.0, 1.0, 0.0],
            [1801, 0.0, 0.0, 1.0],
            [2350, 1.0, 1.0, 1.0],
            [2700, 1.0, 0.0, 0.0],
            [2801, 1.0, 1.0, 0.0]
        ],
        'otf_tuples': [
            [0, 0.0],
            [300, 0.1],
        ],
        'title': 'Temperature'
    },
    'temperature anomaly': {
        'ctf_tuples': [
            [-500, 0.0, 0.0, 1.0],
            [0, 1.0, 1.0, 1.0],
            [500, 1.0, 0.0, 0.0]
        ],
        'otf_tuples': [
            [-10000, 0.0],
            [-500, 0.0],
            [-100, 0.1],
            [0, 0.0001],
            [100, 0.1],
            # [1000, 0.1],
        ],
        'title': 'Anomaly'
    },
    'thermal expansivity': {
        'ctf_tuples': [
            [-4e-8, 0.0, 0.0, 1.0],
            [1e-7, 1.0, 1.0, 1.0],
            [8e-7, 1.0, 0.0, 0.0]
        ],
        'otf_tuples': [
            [-2, 0.0],
            [-1, 0.1],
            # [0, 0.1],
            [1, 0.1],
            # [1000, 0.1],
        ],
        'title': 'Expansivity'
    },
    'thermal conductivity': {
        'ctf_tuples': [
            [-0.05, 0.0, 0.0, 1.0],
            [0.0, 1.0, 1.0, 1.0],
            [0.05, 1.0, 0.0, 0.0]
        ],
        'otf_tuples': [
            [-2, 0.0],
            [-1, 0.01],
            # [0, 0.1],
            [1, 0.01],
            # [1000, 0.1],
        ],
        'title': 'Conductivity'
    },
    'spin transition-induced density anomaly': {
        'ctf_tuples': [
            [-7, 0.0, 0.0, 1.0],
            [0.0, 1.0, 1.0, 1.0],
            [7, 1.0, 0.0, 0.0]
        ],
        'otf_tuples': [
            [-200, 0.0],
            [-100, 0.01],
            # [0, 0.1],
            [100, 0.01],
            # [1000, 0.1],
        ],
        'title': 'Density Anomaly'
    }
}

def get_tf(attr):
    return tf_factory[attr]