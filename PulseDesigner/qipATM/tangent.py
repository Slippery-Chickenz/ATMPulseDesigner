from typing import override
import numpy as np

from .base_pulse import Pulse

class TangentPulse(Pulse):
    """
    Amplitude modulated pulse in the shape of a tangent. Constant frequency and phase.
    """

    def __init__(
        self, 
        time: float, 
        tanCoefficient: float,
        tanFrequency: float,
        tanOffset: float,
        frequency: float, 
        phase: float
    ) -> None:
        super().__init__(time)

        # Ranges for ramping each value
        self.frequency= frequency
        self.tanCoefficient = tanCoefficient
        self.tanFrequency = tanFrequency
        self.tanOffset = tanOffset
        self.phase= phase
        return

    @override
    def getAmplitude(self, t: float) -> float:
        return self.tanCoefficient * np.tan(self.tanFrequency * (t - self.tanOffset))

    @override
    def getFrequency(self, t: float) -> float:
        return self.frequency

    @override
    def getPhase(self, t: float) -> float:
        return self.phase

