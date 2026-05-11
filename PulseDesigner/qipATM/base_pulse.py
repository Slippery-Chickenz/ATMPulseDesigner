import numpy as np
import numpy.typing as npt

import matplotlib.pyplot as plt

class Pulse:

    def __init__(self, time: float) -> None:
        # Total time the pulse takes
        self.time: float = time
        return

    def getAmplitude(self, t: float) -> float:
        """
        Amplitude of the pulse
        """
        raise NotImplementedError("getAmplitude is not implemented")

    def getFrequency(self, t: float) -> float:
        """
        Frequency of the pulse relative to guess larmor
        """
        raise NotImplementedError("getFrequency is not implemented")

    def getPhase(self, t: float) -> float:
        """
        Phase of the pulse
        """
        raise NotImplementedError("getPhase is not implemented")

    def getTime(self) -> float:
        """
        Total time of the pulse
        """
        return self.time

    def getIntegratedFrequencies(
        self, 
        times: npt.NDArray[np.floating]
    ) -> npt.NDArray[np.floating]:
        """
        Frequency of the pulse integrated over its entire time
        """
        # Raw frequencies at each time step
        rawFrequencies = np.array([self.getFrequency(t) for t in times])

        # Integrate the raw frequencies to get the frequency modulated values
        integratedFrequency = np.cumsum(rawFrequencies) * (times[1] - times[0])
        integratedFrequency -= integratedFrequency[-1]
        return integratedFrequency

    def plotPulse(self) -> None:
        """
        Plot the amplitude, frequency, phase, and voltage of the pulse
        """

        # Time values to plot over
        plotTimes = np.linspace(0, self.time, 500)

        # Amplitude, frequency, and pulse values to plot
        amplitudes = [self.getAmplitude(t) for t in plotTimes]
        integratedFrequency = self.getIntegratedFrequencies(plotTimes)
        frequencies = [self.getFrequency(t) for t in plotTimes]
        pulseValues = [self.getAmplitude(t) * np.cos(2 * np.pi * integratedFrequency[i] + self.getPhase((t))) for i, t in enumerate(plotTimes)]

        # Create the fig/axes and set the size
        fig, axes = plt.subplots(nrows=3, ncols=1, layout="tight", sharex=True)
        fig.set_figheight(8)
        fig.set_figwidth(6)
        fig.supxlabel("Time")

        axes[0].plot(plotTimes, amplitudes)
        axes[0].set_ylabel("Amplitude")

        axes[1].plot(plotTimes, frequencies)
        axes[1].set_ylabel("Frequency")

        axes[2].plot(plotTimes, pulseValues)
        axes[2].set_ylabel("Pulse Voltage")
        
        plt.show()
        return
