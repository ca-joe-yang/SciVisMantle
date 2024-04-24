import vtk

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
render_window.AddRenderer(renderer)
render_window.SetSize(800, 400)  # Set the size of the render window

# Define the viewports for the left and right screens
viewport_left = [0.0, 0.0, 0.5, 1.0]    # [xmin, ymin, xmax, ymax]
viewport_right = [0.5, 0.0, 1.0, 1.0]   # [xmin, ymin, xmax, ymax]

# Create a camera
camera = vtk.vtkCamera()

# Create a render window interactor
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Function to synchronize the camera positions between the viewports
def sync_cameras(obj, event):
    # Get the camera position of the main renderer
    camera_position = renderer.GetActiveCamera().GetPosition()
    
    # Set the camera positions for both viewports
    renderer_left.GetActiveCamera().SetPosition(camera_position)
    renderer_right.GetActiveCamera().SetPosition(camera_position)

# Create renderers for left and right viewports
renderer_left = vtk.vtkRenderer()
renderer_left.SetViewport(viewport_left)
renderer_left.SetBackground(0.2, 0.2, 0.2)  # Set a dark gray background for the left viewport
renderer_left.AddActor(actor)  # Add the actor to the left renderer

renderer_right = vtk.vtkRenderer()
renderer_right.SetViewport(viewport_right)
renderer_right.SetBackground(0.2, 0.2, 0.2)  # Set a dark gray background for the right viewport
actor.GetProperty().SetColor(1, 0, 0)  # Set red color for the cube in the right viewport
renderer_right.AddActor(actor)  # Add the actor to the right renderer

# Add both renderers to the render window
render_window.AddRenderer(renderer_left)
render_window.AddRenderer(renderer_right)

# Set the initial camera position
renderer.GetActiveCamera().SetPosition(0, 0, 5)

# Add observer to synchronize cameras
interactor.AddObserver("TimerEvent", sync_cameras)
timer_id = interactor.CreateRepeatingTimer(10)  # 10 milliseconds interval for synchronization

# Start the interaction
interactor.Start()
