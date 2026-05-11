from nicegui import ui
import matplotlib.figure
import matplotlib.axes

class ATMPulsePlot:

    def __init__(self) -> None:

        # Matplotlib plot instance
        self.matplotlibUI: ui.matplotlib | None = None

        # Pulse Figure and axes to plot to
        self.figure: matplotlib.figure.Figure | None = None
        self.axes: list[matplotlib.axes.Axes] | None = None
        return

    def initializePlot(self) -> None:

        with ui.card():
            self.matplotlibUI = ui.matplotlib(figsize=(12,2), layout="tight")

        self.figure = self.matplotlibUI.figure
        self.axes = self.figure.subplots(nrows=1, ncols=3)
        return

    def getAxes(self) -> list[matplotlib.axes.Axes] | None:
        return self.axes
   
    def clearAxes(self) -> None:
        if self.axes is None:
            return
        for ax in self.axes:
           ax.cla()
        return
    
    def drawPlot(self) -> None:

        if self.matplotlibUI is None:
            return
        self.matplotlibUI.update()
        return
    
