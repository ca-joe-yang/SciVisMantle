import vtk
from .utils import lonlatr2xyz

class ClipBorders:

    def __init__(self, lon1, lon2, r, resolution=100, line_width=2):
        self.center = (r, r, r)
        self.r = r
        pt1, pt2, pt3 = self.get_pts(lon1, lon2)

        self.arcs = [
            Arc(pt1, pt2, center=self.center, resolution=resolution, line_width=line_width),
            Arc(pt2, pt3, center=self.center, resolution=resolution, line_width=line_width),
            Arc(pt1, pt3, center=self.center, resolution=resolution, line_width=line_width)
        ]

        self.lines = [
            Line(pt1, self.center, resolution=resolution, line_width=line_width),
            Line(pt2, self.center, resolution=resolution, line_width=line_width),
            Line(pt3, self.center, resolution=resolution, line_width=line_width)
        ]

        self.actors = [ arc.actor for arc in self.arcs ]
        self.actors += [ line.actor for line in self.lines ]

    def get_pts(self, lon1, lon2):
        x1, y1, z1 = lonlatr2xyz(90-lon1, 90, self.r)
        pt1 = x1+self.r, y1+self.r, z1+self.r
        
        x2, y2, z2 = lonlatr2xyz(90-lon1, 0, self.r)
        pt2 = x2+self.r, y2+self.r, z2+self.r
        
        x3, y3, z3 = lonlatr2xyz(90-lon2, 0, self.r)
        pt3 = x3+self.r, y3+self.r, z3+self.r

        return pt1, pt2, pt3
    
    def Update(self, lon1, lon2):
        pt1, pt2, pt3 = self.get_pts(lon1, lon2)
        
        self.arcs[0].Update(pt1, pt2)
        self.arcs[1].Update(pt2, pt3)
        self.arcs[2].Update(pt1, pt3)

        self.lines[0].Update(pt1, self.center)
        self.lines[1].Update(pt2, self.center)
        self.lines[2].Update(pt3, self.center)

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

    def Update(self, pt1, pt2):
        self.source.SetPoint1(*pt1)     
        self.source.SetPoint2(*pt2)  

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

    def Update(self, pt1, pt2):
        self.source.SetPoint1(*pt1)     
        self.source.SetPoint2(*pt2)  