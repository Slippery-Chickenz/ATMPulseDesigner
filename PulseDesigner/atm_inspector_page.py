from nicegui import ui
import numpy as np

import os

from .qipATM import ATMGate

from .atm_parameter_input import ATMParamaterInput
from .atm_pulse_plot import ATMPulsePlot
from .atm_detuning_plot import ATMDetuningPlot

class ATMInspectorPage:

    def __init__(self) -> None:

        # ATM Pulse currently inspected
        self.atmGate: ATMGate | None = None

        # Percentage value for rise and fall gradients to put in the save data
        self.percentRiseGradient: float | None = None
        self.percentFallGradient: float | None = None

        # Paramater Input
        self.atmParameterInput: ATMParamaterInput = ATMParamaterInput(self.updatePulse, self.savePulse)

        # Plots
        self.atmPulsePlot: ATMPulsePlot = ATMPulsePlot()

        self.atmDetuningPlot: ATMDetuningPlot = ATMDetuningPlot()

        self.initializeInspectorPage()
        return

    def initializeInspectorPage(self):
        @ui.page("/")
        def inspectorPage():
            with ui.grid(rows = '1fr 2fr', columns = '200px 1fr'):
                self.atmParameterInput.initializeParameterInput()

                self.atmPulsePlot.initializePlot()
                self.atmDetuningPlot.initializePlot()
            return
        return

    def updatePulse(
        self,
        pulseTime: float | None,
        riseTime: float | None,
        fallTime: float | None,
        maxAmplitude: float | None,
        maxFrequency: float | None,
        riseGradient: float | None,
        fallGradient: float | None
    ) -> None:

        if (pulseTime is None or
            riseTime is None or
            fallTime is None or
            maxAmplitude is None or
            maxFrequency is None or
            riseGradient is None or
            fallGradient is None):
            print("Tried to update pulse missing a parameter")
            return;

        self.percentFallGradient = fallGradient
        self.percentRiseGradient = riseGradient
        
        # Convert rise and fall gradient to absolute instead of relative values
        riseGradient = maxAmplitude * riseGradient / riseTime
        fallGradient = maxAmplitude * fallGradient / fallTime
                
        # Multiplying this by 2 because the amplitude is taken as the lab frame amplitude but our experimental setups give rotating frame
        maxAmplitude *= 2 

        try:
            self.atmGate = ATMGate(pulseTime,
                                   riseTime,
                                   fallTime,
                                   maxAmplitude,
                                   maxFrequency,
                                   riseGradient,
                                   fallGradient)
        except:
            print("Cannot calculate ATM Pulse with these values")
            ui.notify("Cannot calculate ATM Pulse with these values")
            self.atmPulseGate = None
            return

        self.atmPulsePlot.clearAxes()
        self.atmGate.plotPulses(self.atmPulsePlot.getAxes())
        self.atmPulsePlot.drawPlot()


        # Set the new detuning and find a range of values to test
        self.atmDetuningPlot.setATM(self.atmGate)
        return

    def savePulse(
        self,
        fileName: str | None,
    ) -> None:

        self.atmParameterInput.collectAndUpdate()

        if self.atmGate is None:
            print("No Valid ATM Pulse currently made")
            return

        if fileName is None:
            print("No given file name")
            return

        # If a file extension was given then remove it and save it
        name, extension = os.path.splitext(fileName)
        if extension == "":
            extension = ".txt"

        pulseData = self.atmGate.getPulseData()

        for i, side in enumerate(["_left_", "_right_"]):
            for j, iq, in enumerate(["I", "Q"]):
                with open(name + 
                          side + 
                          iq + extension, "w") as f:
                    for pulseValue in pulseData[i][j]:
                        f.write("{:f}".format(float(np.float16(pulseValue))) + "\n")
        
        with open(name + "_params.txt", "w") as f:
            f.write("Pulse Time: {}\n".format(self.atmGate.getTime()))
            f.write("Rise Time: {}\n".format(self.atmGate.riseTime))
            f.write("Fall Time: {}\n".format(self.atmGate.fallTime))
            f.write("Max Amplitude: {}\n".format(self.atmGate.getMaxAmplitude() / 2))
            f.write("Max Frequency: {}\n".format(self.atmGate.getMaxFrequency()))
            f.write("Percent Rise Gradient: {}\n".format(self.percentRiseGradient))
            f.write("Percent Gradient: {}\n".format(self.percentFallGradient))
            f.write("Rise Gradient: {}\n".format(self.atmGate.riseGradient))
            f.write("Fall Gradient: {}".format(self.atmGate.fallGradient))
        return
