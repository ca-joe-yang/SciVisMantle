import vtk

class Axes:

    def __init__(self, length=10):
        self.actor = vtk.vtkAxesActor()
        # self.actor.SetShaftTypeToCylinder()
        self.actor.SetXAxisLabelText('X')
        self.actor.SetYAxisLabelText('Y')
        self.actor.SetZAxisLabelText('Z')
        self.actor.SetTotalLength(length, length, length)
        # self.actor.SetCylinderRadius(0.5 * self.actor.GetCylinderRadius())
        # self.actor.SetConeRadius(1.025 * self.actor.GetConeRadius())
        # self.actor.SetSphereRadius(1.5 * self.actor.GetSphereRadius())

        xAxisLabel = self.actor.GetXAxisCaptionActor2D()
        xAxisLabel.GetTextActor().SetTextScaleModeToNone()
        xAxisLabel.GetCaptionTextProperty().SetFontSize(10)
        xAxisLabel.GetCaptionTextProperty().SetColor(1, 0, 0)

        yAxisLabel = self.actor.GetYAxisCaptionActor2D()
        yAxisLabel.GetTextActor().SetTextScaleModeToNone()
        yAxisLabel.GetCaptionTextProperty().SetFontSize(10)
        yAxisLabel.GetCaptionTextProperty().SetColor(0, 1, 0)

        zAxisLabel = self.actor.GetZAxisCaptionActor2D()
        zAxisLabel.GetTextActor().SetTextScaleModeToNone()
        zAxisLabel.GetCaptionTextProperty().SetFontSize(10)
        zAxisLabel.GetCaptionTextProperty().SetColor(0, 0, 1)