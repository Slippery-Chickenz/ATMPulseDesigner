from nicegui import ui
import numpy as np

from .qipATM import ATMGate

from .atm_parameter_input import ATMParamaterInput
from .atm_pulse_plot import ATMPulsePlot
from .atm_detuning_plot import ATMDetuningPlot

class ATMInspectorPage:

    def __init__(self) -> None:

        # ATM Pulse currently inspected
        self.atmGate: ATMGate | None = None

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
        pulseTime: float,
        riseTime: float,
        fallTime: float,
        maxAmplitude: float,
        maxFrequency: float,
        riseGradient: float,
        fallGradient: float
    ) -> None:
        
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
        fileName: str,
    ) -> None:

        if self.atmGate is None:
            print("No Valid ATM Pulse currently made")
            return

        pulseData = self.atmGate.getPulseData()

        print(fileName)
        with open(fileName, "w") as f:
            f.write("Rabi={}\n".format(self.atmGate.getMaxAmplitude()))
            f.write("leftI,leftQ,rightI,rightQ\n")
            for k in range(len(pulseData[0][0])):
                dataString = ""
                for i in range(2):
                    for j in range(2):
                        dataString += "{:f},".format(float(np.float16(pulseData[i][j][k])))
                dataString = dataString[:-1]
                dataString += "\n"
                f.write(dataString)

        return
