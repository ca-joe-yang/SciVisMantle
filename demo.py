import vtk

# Create some example vtkPolyData
points = vtk.vtkPoints()
points.InsertNextPoint(0, 0, 0)
points.InsertNextPoint(1, 0, 0)
points.InsertNextPoint(1, 1, 0)
points.InsertNextPoint(0, 1, 0)

polygon = vtk.vtkPolygon()
polygon.GetPointIds().SetNumberOfIds(4)
for i in range(4):
    polygon.GetPointIds().SetId(i, i)

cells = vtk.vtkCellArray()
cells.InsertNextCell(polygon)

polydata = vtk.vtkPolyData()
polydata.SetPoints(points)
# polydata.SetPolys(cells)

# Create a mapper
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputData(polydata)

# Create an actor
actor = vtk.vtkActor()
actor.SetMapper(mapper)

# Create a renderer
renderer = vtk.vtkRenderer()
renderer.SetBackground(0.1, 0.2, 0.4)

# Add actor to the renderer
renderer.AddActor(actor)

# Create a render window
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)

# Create a render window interactor
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Start the rendering loop
render_window.Render()
interactor.Start()