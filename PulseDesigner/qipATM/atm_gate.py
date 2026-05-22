import numpy as np
from scipy.optimize import root_scalar

import matplotlib.axes
import matplotlib.pyplot as plt

from typing import Literal

from .ramp import RampPulse
from .tangent import TangentPulse
from .base_pulse import Pulse

class ATMGate:
    """
    Quantum gate defining an ATM pulse
    """

    def __init__(
        self, 
        time: float, 
        riseTime: float, 
        fallTime: float,
        maxAmplitude: float,
        maxFrequency: float,
        riseGradient: float,
        fallGradient: float,
    ) -> None:
        """
        Initialize ATM Pulse Gate.
        Parameters:
        - time: Total time of the pulse.
        - riseTime: Time of the rising edge.
        - fallTime: Time of the falling edge.
        - ampMax: Maximum amplitude of the pulse.
        - freqMax: Maximum frequency of the pulse.
        - riseGradient: Gradient for the rising edge.
        - fallGradient: Gradient for the falling edge.
        """
        super().__init__()

        # List of pulses that constitute this gate
        self.pulses: list[Pulse] = []

        # Find the coefficient and frequency of the tangent portions of the pulse
        riseB: float = self._findBeta(riseTime, riseGradient, maxAmplitude)
        riseA: float = riseGradient / riseB

        fallB: float = self._findBeta(-fallTime, -fallGradient, maxAmplitude)
        fallA: float = fallGradient / fallB

        self.riseTime: float = riseTime
        self.fallTime: float = fallTime
        self.maxFrequency: float = maxFrequency
        self.maxAmplitude: float = maxAmplitude
        self.riseGradient: float = riseGradient
        self.fallGradient: float = fallGradient

        # Append each portion of the pulse
        self.appendPulse(TangentPulse(riseTime, riseA, riseB, 0, maxFrequency, 0))
        self.appendPulse(RampPulse(time - riseTime - fallTime, 
                                   (maxAmplitude, maxAmplitude), 
                                   (maxFrequency, 0), 
                                   (0, 0)))
        self.appendPulse(TangentPulse(fallTime, -fallA, fallB, fallTime, 0, 0))
        return

    def getPulseData(
        self
    ) -> tuple[tuple[list[float], list[float]], tuple[list[float], list[float]]]:
        """
        Get the IQ Pulse data for the left and right (positive and negative frequency) side of this ATM Pulse
        """

        leftIQ = ATMGate(self.getTime(), 
                          self.riseTime,
                          self.fallTime,
                          self.maxAmplitude,
                          self.maxFrequency,
                          self.riseGradient,
                          self.fallGradient).getGateWaveform()
        rightIQ = ATMGate(self.getTime(), 
                          self.riseTime,
                          self.fallTime,
                          self.maxAmplitude,
                          -self.maxFrequency,
                          self.riseGradient,
                          self.fallGradient).getGateWaveform()

        scaledLeft = ([i / self.maxAmplitude for i in leftIQ[0]],
                      [i / self.maxAmplitude for i in leftIQ[1]])
        scaledRight = ([i / self.maxAmplitude for i in rightIQ[0]],
                       [i / self.maxAmplitude for i in rightIQ[1]])

        return scaledLeft, scaledRight

    def getGateWaveform(
        self, 
        timeUnitConversion: float = 1e3
    ) -> tuple[list[float], list[float]]:

        # Time values to save at (Should be in nano seconds)
        saveTimes = np.linspace(0, self.getTime(), int(self.getTime() * timeUnitConversion))

        # Amplitude, frequency, and pulse values to plot
        pulseTimes = np.linspace(0, self.getTime(), int(self.getTime() * 1000))
        integratedFrequency = [0]
        for t in pulseTimes:
            integratedFrequency.append(integratedFrequency[-1] + self.getFrequency(float(t)) * pulseTimes[1])
        integratedFrequency.pop()
        integratedFrequency = [i - integratedFrequency[-1] for i in integratedFrequency]
        pulseValues = [self.getAmplitude(t) * 
                        np.exp((2 * np.pi * integratedFrequency[i]
                        + self.getPhase(t)) * -1j)
                        for i, t in enumerate(saveTimes)]
        pulseValuesI = [val.real for val in pulseValues]
        pulseValuesQ = [val.imag for val in pulseValues]
        return pulseValuesI, pulseValuesQ

    def _findBeta(self, t: float, gradient: float, maxAmplitude: float) -> float:
        """
        Calculate b for y = A*tan(b*x) given a maximum amplitude and starting gradient
        """

        # Function to find the roots of to find Beta to ensure the
        # Tangent sections line up with the constant
        def funcToSolve(B) -> float:
            return np.arctan((B * maxAmplitude)/gradient) - B*t

        lowerBoundB = 1e-10
        upperBoundB = 15

        if funcToSolve(lowerBoundB) * funcToSolve(upperBoundB) > 0:
            raise ValueError("The given parameters are impossible to find a tangent function to satisfy")

        sol = root_scalar(funcToSolve, bracket=(1e-10, 15), method='brentq')
        return sol.root

    def getMaxFrequency(self) -> float:
        return self.maxFrequency

    def getMaxAmplitude(self) -> float:
        return self.maxAmplitude

    def getPulseParameters(self) -> dict[str, float]:
        """
        Get the 7 parameters that define this ATM Pulse
        """
        params: dict[str, float] = {}

        params["Total Time (us)"] = self.getTime()
        params["Rise Time (us)"] = self.riseTime
        params["Fall Time (us)"] = self.fallTime
        params["Max Frequency (MHz)"] = self.maxFrequency
        params["Max Amplitude (MHz)"] = self.maxAmplitude
        params["Rise Gradient"] = self.riseGradient
        params["Fall Gradient"] = self.fallGradient
        return params

    def getAmplitude(self, t: float) -> float:
        pulse, pulseTime = self.getPulse(t)
        return pulse.getAmplitude(pulseTime)
    def getFrequency(self, t: float) -> float:
        pulse, pulseTime = self.getPulse(t)
        return pulse.getFrequency(pulseTime)
    def getPhase(self, t: float) -> float:
        pulse, pulseTime = self.getPulse(t)
        return pulse.getPhase(pulseTime)

    def appendPulse(self, newPulse: Pulse) -> None:
        self.pulses.append(newPulse)
    def getPulse(self, t) -> tuple[Pulse, float]:
        for pulse in self.pulses:
            if t < pulse.getTime():
                return pulse, t
            t -= pulse.getTime()
        return self.pulses[-1], self.pulses[-1].getTime()

    def getTime(self) -> float:
        t = 0
        for pulse in self.pulses:
            t += pulse.getTime()
        return t

    def plotPulses(self, axes: list[matplotlib.axes.Axes] | None = None, orientation: Literal["h", "v"] = "v") -> None:

        # Time values to plot over
        plotTimes = np.linspace(0, self.getTime(), 500 * len(self.pulses))

        # Amplitude, frequency, and pulse values to plot
        amplitudes = [self.getAmplitude(t) / 2 for t in plotTimes]
        integratedFrequency = [0]
        for t in plotTimes:
            integratedFrequency.append(integratedFrequency[-1] + self.getFrequency(t) * plotTimes[1])
        integratedFrequency.pop()
        integratedFrequency = [i - integratedFrequency[-1] for i in integratedFrequency]
        frequencies = [self.getFrequency(t) for t in plotTimes]
        pulseValues = [self.getAmplitude(t) * np.cos(2 * np.pi * integratedFrequency[i] + self.getPhase((t))) for i, t in enumerate(plotTimes)]

        showPlot = False

        # Create the fig/axes and set the size
        if axes is None:
            showPlot = True
            nrows = 3
            ncols = 1
            if orientation == "h":
                nrows = 1
                ncols = 3
            fig, axes = plt.subplots(nrows=nrows, ncols=ncols, layout="tight", sharex=True)
            fig.set_figheight(12)
            fig.set_figwidth(6)
            if orientation == "h":
                fig.set_figheight(4)
                fig.set_figwidth(15)
            fig.supxlabel("Time ($\\mu$s)")

        if axes is None:
            raise TypeError("Something went wrong and Axes are not defined")

        axes[0].plot(plotTimes, amplitudes)
        axes[0].set_ylabel("Amplitude")

        axes[1].plot(plotTimes, frequencies)
        axes[1].set_ylabel("Frequency")

        axes[2].plot(plotTimes, pulseValues)
        axes[2].set_ylabel("Pulse")
        
        if showPlot:
            plt.show()

        return
