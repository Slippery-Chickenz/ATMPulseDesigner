from nicegui import ui

import numpy as np
import random

import matplotlib.figure, matplotlib.axes, matplotlib.lines

from .qipATM import ATMGate, ATMDetuneResponse

class ATMDetuningPlot:
    """
    Class to create and update ATM Pulse Detuning Response
    """

    def __init__(self) -> None:
        """
        Initialize the class with empty values
        """

        # Detuning response
        self.detuningResponse: ATMDetuneResponse = ATMDetuneResponse()
        self.resetResponseCalculation()
        
        # Detuning response values to plot
        self.detuningValues: list[float] = []
        self.detuningProbabilities: list[float] = []
        self.atmSensitivity: float = -1
        self.atmRange: float = -1

        # Matplotlib plot instance
        self.matplotlibUI: ui.matplotlib | None = None
        self.plotUpdateTime: ui.timer | None = None

        # Pulse Figure and axes to plot to
        self.figure: matplotlib.figure.Figure | None = None
        self.axes: matplotlib.axes.Axes | None = None

        # Response Lines
        self.rightResponseLine: matplotlib.lines.Line2D | None = None
        self.leftResponseLine: matplotlib.lines.Line2D | None = None

        # Sensitivity and Range Guide Lines
        self.sensitivityLine: matplotlib.lines.Line2D | None = None
        self.rangeLine: matplotlib.lines.Line2D | None = None
        self.toleranceLine: matplotlib.lines.Line2D | None = None
        return

    def initializePlot(self) -> None:
        """
        Initialize the nicegui UI elements for the plot
        """

        # Make a background card and matplotlib plot
        with ui.card():
            self.matplotlibUI = ui.matplotlib(figsize=(12,4))

        # Get figure and axes for the plot
        self.figure = self.matplotlibUI.figure
        self.axes = self.figure.subplots(nrows=1, ncols=1)

        # Nicegui timer for updating the plot
        self.plotUpdateTime = ui.timer(0.1, 
                                       self.updatePlot, 
                                       active=False, 
                                       immediate=False)
        return

    def setATM(self, newATM: ATMGate) -> None:
        """
        Set a new ATM gate and start updating the plot with new values
        """

        # If the new ATM pulse is the same as the previous then do not reset anything
        if self.detuningResponse.compareATM(newATM):
            return

        # If there is no plot update timer made yet then return
        if self.plotUpdateTime is None:
            return

        # Deactivate the update timer and reset the calculation
        self.plotUpdateTime.deactivate()
        self.resetResponseCalculation()

        # Make a list of detuning values to calculate flip probability for
        allValues = np.linspace(-newATM.getMaxFrequency() * 1.25,
                                newATM.getMaxFrequency() * 0.1,
                                1000)
        allValues = np.concat((allValues, 
                              np.linspace(-newATM.getMaxFrequency() * 0.1, 
                              newATM.getMaxFrequency() * 0.1,
                              1000)))
        allValues = np.concat((allValues, 
                              np.linspace(-newATM.getMaxFrequency() * 0.1, 
                              newATM.getMaxFrequency() * 1.25,
                              1000)))
        self.detuningValues = random.sample(allValues.tolist(), len(allValues))

        # Set the atm pulse to the new one and start testing detuning values
        self.detuningResponse.setATM(newATM)
        self.detuningResponse.testDetuningAsync(self.detuningValues)


        # Reset the plot and restart the update timer
        self.drawPlot()
        self.plotUpdateTime.activate()
        return

    def resetResponseCalculation(self) -> None:
        """
        Terminate the asynchronous calculation and remake the pool
        """
        self.detuningResponse.terminateAsync()
        self.detuningResponse = ATMDetuneResponse(2)
        return

    def updatePlot(self) -> None:
        """
        Update the plot with any new data that has been calculated
        """

        # Collect any new response data calculated
        responseData = self.detuningResponse.getResponse()
        self.detuningValues = responseData[0]
        self.detuningProbabilities = responseData[1]
        self.atmSensitivity = responseData[2]
        self.atmRange = responseData[3]

        # If any of the plot elements have not been made yet then return
        if (self.figure is None or
            self.axes is None or
            self.rightResponseLine is None or
            self.sensitivityLine is None or
            self.rangeLine is None):
            return

        # Update the response line with new data
        self.rightResponseLine.set_ydata(self.detuningProbabilities)
        self.rightResponseLine.set_xdata(self.detuningValues)

        # Update the sensitivity and range line
        self.sensitivityLine.set_xdata([self.atmSensitivity/2, self.atmSensitivity/2])
        self.rangeLine.set_xdata([self.atmRange/2, self.atmRange/2])

        # Update the legend
        newLabels = ["Sens: {:.2f} kHz".format(self.atmSensitivity * 1000),
                     "Range: {:.3f} MHz".format(self.atmRange),
                     "Tol: {:.2f}".format(self.detuningResponse.tolerance)]

        self.axes.legend(handles=[self.sensitivityLine, 
                                  self.rangeLine, 
                                  self.toleranceLine],
                         labels=newLabels)

        # Redraw the figure
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

        # Update drawing in the UI
        if self.matplotlibUI is None:
            return
        self.matplotlibUI.update()
        return

    def drawPlot(self) -> None:
        """
        Draw the empty plot and initialize all the lines to be updated
        """

        if self.axes is None:
            return

        # Clear old contents
        self.axes.clear()

        # Set Labels
        self.axes.set_xlabel("Detuning (MHz)")
        self.axes.set_ylabel("Probability")

        # Set the limits and draw guide lines
        self.axes.set_ylim(ymin=-0.05, ymax=1.05)
        self.axes.set_xlim(xmin=min(self.detuningValues), xmax=max(self.detuningValues))

        self.detuningValues = []
        self.detuningProbabilities = []

        # Draw response line
        self.rightResponseLine = self.axes.plot(self.detuningValues, 
                                                self.detuningProbabilities)[0]

        # Draw guide lines
        self.axes.axvline(0, 0, 1, alpha=0.5, linestyle="--")
        self.sensitivityLine = self.axes.axvline(0, 0, 1, 
                                                 alpha=0.5, 
                                                 linestyle="--",
                                                 label="Sens: ")
        self.rangeLine = self.axes.axvline(0, 0, 1, 
                                           alpha=0.5, 
                                           linestyle="--", label="Range: ")
        self.toleranceLine = self.axes.axhline(0.9, 
                                               0, 1, 
                                               alpha=0.5, 
                                               linestyle="--", 
                                               label="Tol: 0.9")
        self.axes.axhline(1, 0, 1, 
                          alpha=0.5, 
                          linestyle="--")
        
        # Update drawing in UI
        if self.matplotlibUI is None:
            return
        self.matplotlibUI.update()
        return
    
