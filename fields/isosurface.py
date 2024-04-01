import vtk

class Isosurface:

    def __init__(self, data, iso_value, rgb, alpha):
        self.surface = vtk.vtkContourFilter()
        self.surface.SetInputData(data)
        self.surface.SetValue(0, iso_value)

        # print(self.surface)
            
        self.mapper = vtk.vtkDataSetMapper()
        self.mapper.ScalarVisibilityOn()
        self.mapper.SetInputConnection(self.surface.GetOutputPort())

        self.actor = vtk.vtkActor()
        self.actor.SetMapper(self.mapper)
        # self.actor.GetProperty().SetOpacity(alpha)
        # self.actor.GetProperty().SetColor(*rgb)
