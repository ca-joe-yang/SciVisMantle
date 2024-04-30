import vtk
import time

class MyTimerCallback:
    def __init__(self):
        self.timer_count = 0
    
    def execute(self, obj, event):
        print("Timer event triggered:", self.timer_count)
        self.timer_count += 1
        # Optionally, change the timer interval based on conditions
        # obj creates the timer, so you can modify it here
        obj.CreateRepeatingTimer(1000)  # Set a new timer interval of 1000 milliseconds
        time.sleep(1)

# Create a vtkRenderer, vtkRenderWindow, and vtkRenderWindowInteractor
renderer = vtk.vtkRenderer()
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Create a callback object
callback = MyTimerCallback()

# Set up a timer and associate it with the callback
timer_id = interactor.CreateRepeatingTimer(1000)  # Set the initial timer interval to 500 milliseconds
interactor.AddObserver("TimerEvent", callback.execute)

# Start the interactor
interactor.Start()
