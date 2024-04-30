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
        self.bar.scalar_bar.SetLabelFormat("%-#6.1e")

        if mode == 'right':
            self.bar.set_position((0.8, 0.5))
        elif mode == 'left':
            self.bar.set_position((0.1, 0.5))

    def Update(self, attr):
        tf_cfg = tf_factory[attr]
        ctf_tuples = tf_cfg['ctf_tuples']
        title = tf_cfg['title']

        self.ctf.RemoveAllPoints()
        for ctf_tuple in ctf_tuples:
            self.ctf.AddRGBPoint(*ctf_tuple)

        if 'otf_tuples' in tf_cfg:
            otf_tuples = tf_cfg['otf_tuples']
            self.otf.RemoveAllPoints()
            for otf_tuple in otf_tuples:
                self.otf.AddPoint(*otf_tuple)

        self.bar.set_title(title=title, size=10)

tf_factory = {
    'temperature': {
        'ctf_tuples': [
            [0, 0.0, 0.0, 0.0],
            [1500, 0.0, 0.0, 1.0],
            [2350, 1.0, 1.0, 0.0],
            [2000, 0.0, 1.0, 0.0],
            [2500, 1.0, 0.0, 0.0]
        ],
        'otf_tuples': [
            [0, 0.0],
            [300, 1],
        ],
        'title': 'Temperature'
    },
    'temperature anomaly': {
        'ctf_tuples': [
            [-500, 0.0, 0.0, 1.0],
            [0, 0.0, 1.0, 0.0],
            [500, 1.0, 0.5, 0.0],
            [1000, 1.0, 0.0, 0.0]
        ],
        'otf_tuples': [
            [-10000, 0.0],
            [-500, 0.1],
            # [-100, 0.1],
            [0, 0.0001],
            [500, 0.1],
            # [1000, 0.1],
        ],
        'title': 'Anomaly'
    },
    'thermal expansivity': {
        'ctf_tuples': [
            [0, 0.0, 0.0, 1.0],
            [4e-7, 1.0, 1.0, 1.0],
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
    },
    'magnitude': {
        'ctf_tuples': [
            [0, 0.0, 0.0, 1.0],
            [2.5e-9, 1.0, 1.0, 1.0],
            [5e-9, 1.0, 0.0, 0.0]
        ],
        'title': 'Magnitude'
    }

    # self.ctf = vtk.vtkColorTransferFunction()
    #     # ctf.AddRGBPoint(minScalarValue, 0.001462, 0.000466, 0.013866)
    #     # ctf.AddRGBPoint((minScalarValue + maxScalarValue) / 2, 0.365953, 0.146965, 0.472712)
    #     # ctf.AddRGBPoint(maxScalarValue, 0.988362, 0.998364, 0.644924)
    #     self.ctf.AddRGBPoint(minScalarValue, 0.001462, 0.000466, 0.013866)
    #     self.ctf.AddRGBPoint((minScalarValue + maxScalarValue) / 2, 0.365953, 0.146965, 0.472712)
    #     self.ctf.AddRGBPoint(maxScalarValue, 0.988362, 0.998364, 0.644924)
}

def get_tf(attr):
    return tf_factory[attr]