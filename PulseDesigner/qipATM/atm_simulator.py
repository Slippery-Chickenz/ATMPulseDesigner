from os import stat
import numpy as np
import numpy.typing as npt

from scipy.linalg import expm

from .atm_gate import ATMGate

PAULIX: npt.NDArray[np.complexfloating] = np.array([[0,   1], [ 1,  0]])
PAULIY: npt.NDArray[np.complexfloating] = np.array([[0, -1j], [1j,  0]])
PAULIZ: npt.NDArray[np.complexfloating] = np.array([[1,   0], [ 0, -1]])

SX: npt.NDArray[np.complexfloating] = PAULIX / 2
SY: npt.NDArray[np.complexfloating] = PAULIY / 2
SZ: npt.NDArray[np.complexfloating] = PAULIZ / 2

class ATMSimulator:

    def __init__(self, atm_gate: ATMGate, detuning_value: float) -> None:

        self.gate: ATMGate = atm_gate
        self.detuning: float = detuning_value

        self.dt = 0.1
        return

    def simulateCircuit(
        self
    ) -> float:

        starting_state = np.array(([1.0, 0.0]))
        evolutionOperator = self.getEvolutionOperator()

        starting_state =  evolutionOperator @ starting_state
        return np.real(starting_state[1] * np.conj(starting_state[1]))

    def getEvolutionOperator(
        self
    ) -> npt.NDArray[np.complexfloating]:

        # Evolution operator, Hamiltonian, and detuning term
        evolutionOperator: npt.NDArray[np.complexfloating]
        hamiltonian: npt.NDArray[np.complexfloating]
        detuningTerm: npt.NDArray[np.complexfloating]

        # Evolution operator for the given circuit
        evolutionOperator = np.eye(2, dtype = "complex")

        # Diagonal term in the interaction frame
        # Splitting of the spin states based on detuning
        detuningTerm: npt.NDArray[np.complexfloating] = np.array([[-self.detuning * np.pi, 0], [0, self.detuning * np.pi]], dtype=complex)

        frequency: float = 0

        # Loop over the entire time of the circuit
        for t in np.arange(0, self.gate.getTime(), self.dt):

            hamiltonian: npt.NDArray[np.complexfloating] = np.zeros((2, 2), dtype="complex")

            amplitude = self.gate.getAmplitude(float(t))
            frequency += self.gate.getFrequency(float(t)) * self.dt
            phase = self.gate.getPhase(float(t))

            hamiltonian += ((amplitude * np.pi) * 
                           (np.cos(2 * np.pi * frequency + phase) * SX - 
                            np.sin(2 * np.pi * frequency + phase) * SY))

            hamiltonian -= detuningTerm
            evolutionOperator = (evolutionOperator.dot(expm(-1j 
                                 *self.dt
                                 *hamiltonian)))
        return evolutionOperator





