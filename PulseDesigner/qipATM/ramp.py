from typing import override
from .base_pulse import Pulse

class RampPulse(Pulse):

    def __init__(self, time: float, amplitudeRange: tuple[float, float],
                                    frequencyRange: tuple[float, float], 
                                    phaseRange: tuple[float, float]) -> None:
        super().__init__(time)

        # Ranges for ramping each value
        self.frequencyRange = frequencyRange
        self.amplitudeRange = amplitudeRange
        self.phaseRange = phaseRange
        return

    @override
    def getAmplitude(self, t: float) -> float:
        return (t * ((self.amplitudeRange[1] - self.amplitudeRange[0]) / self.time)) + self.amplitudeRange[0]

    @override
    def getFrequency(self, t: float) -> float:
        return (t * ((self.frequencyRange[1] - self.frequencyRange[0]) / self.time)) + self.frequencyRange[0]

    @override
    def getPhase(self, t: float) -> float:
        return (t * ((self.phaseRange[1] - self.phaseRange[0]) / self.time)) + self.phaseRange[0]
