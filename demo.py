import vtk
import numpy as np

# Custom camera to show only left side of the camera view
class CustomCamera(vtk.vtkCamera):
    def ViewTransformMatrix(self):
        # Get the default view transform matrix
        matrix = vtk.vtkMatrix4x4()
        matrix.DeepCopy(super().ViewTransformMatrix())

        # Modify the matrix to pan the camera to the left side
        matrix.SetElement(0, 3, -1.0)  # Translate along the X-axis to the left side
        matrix.SetElement(1, 3, 0.0)   # No translation along the Y-axis
        matrix.SetElement(2, 3, 0.0)   # No translation along the Z-axis

        return matrix

# Create a cube source
cube_source = vtk.vtkCubeSource()

# Create a mapper
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(cube_source.GetOutputPort())

# Create an actor
actor = vtk.vtkActor()
actor.SetMapper(mapper)

# Create a renderer
renderer = vtk.vtkRenderer()
renderer.SetBackground(0.8, 0.8, 0.8)  # Set a light gray background

# Add the cube actor to the renderer
renderer.AddActor(actor)

# Create a render window
render_window = vtk.vtkRenderWindow()
render_window.SetSize(800, 400)  # Set the size of the render window

# Create a renderer for the left side
renderer_left = vtk.vtkRenderer()
# renderer_left.SetViewport(0.0, 0.0, 0.5, 1.0)  # Set viewport for the left half
renderer_left.SetBackground(0.8, 0.8, 0.8)  # Set a light gray background for the left viewport
renderer_left.AddActor(actor)  # Add the actor to the left renderer

# Add the left renderer to the render window
render_window.AddRenderer(renderer_left)

# Create a render window interactor
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Create a custom camera for the left renderer
custom_camera = CustomCamera()
renderer_left.SetActiveCamera(custom_camera)

# Start the interaction
interactor.Start()
