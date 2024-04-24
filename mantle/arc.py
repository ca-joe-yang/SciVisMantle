import vtk
from .utils import lonlatr2xyz

class ClipBorders:

    def __init__(self, lon1, lon2, r, resolution=100, line_width=2):
        x1, y1, z1 = lonlatr2xyz(90-lon1, 90, r)
        pt1 = x1+r, y1+r, z1+r
        
        x2, y2, z2 = lonlatr2xyz(90-lon1, 0, r)
        pt2 = x2+r, y2+r, z2+r
        
        x3, y3, z3 = lonlatr2xyz(90-lon2, 0, r)
        pt3 = x3+r, y3+r, z3+r

        center = (r, r, r)

        self.arcs = [
            Arc(pt1, pt2, center=(r, r, r), resolution=resolution, line_width=line_width),
            Arc(pt2, pt3, center=(r, r, r), resolution=resolution, line_width=line_width),
            Arc(pt1, pt3, center=(r, r, r), resolution=resolution, line_width=line_width)
        ]

        self.lines = [
            Line(pt1, center, resolution=resolution, line_width=line_width),
            Line(pt2, center, resolution=resolution, line_width=line_width),
            Line(pt3, center, resolution=resolution, line_width=line_width)
        ]

        self.actors = [ arc.actor for arc in self.arcs ]
        self.actors += [ line.actor for line in self.lines ]

class Arc:

    def __init__(self, pt1, pt2, center=(0,0,0), resolution=100, line_width=5):
        self.source = vtk.vtkArcSource()
        self.source.SetCenter(*center)  # Center of the arc
        self.source.SetPoint1(*pt1)   # Start point of the arc        
        self.source.SetPoint2(*pt2)   # End point of the arc
        self.source.SetResolution(resolution)   # Resolution of the arc (number of points)

        # Create a mapper
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(self.source.GetOutputPort())

        # Create an actor
        self.actor = vtk.vtkActor()
        self.actor.SetMapper(self.mapper)
        self.actor.GetProperty().SetColor(0, 0, 0)  # Set color of the arc (e.g., red)

        # Set the width of the line representing the arc
        self.actor.GetProperty().SetLineWidth(line_width)


class Line:

    def __init__(self, pt1, pt2, resolution=100, line_width=5):
        self.source = vtk.vtkLineSource()
        self.source.SetPoint1(*pt1)   # Start point of the line        
        self.source.SetPoint2(*pt2)   # End point of the line
        self.source.SetResolution(resolution)   # Resolution of the line (number of points)

        # Create a mapper
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(self.source.GetOutputPort())

        # Create an actor
        self.actor = vtk.vtkActor()
        self.actor.SetMapper(self.mapper)
        self.actor.GetProperty().SetColor(0, 0, 0)  # Set color of the arc (e.g., red)

        # Set the width of the line representing the arc
        self.actor.GetProperty().SetLineWidth(line_width)