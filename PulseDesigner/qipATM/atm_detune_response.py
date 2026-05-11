import numpy as np
import matplotlib.axes

import copy
from multiprocessing import Manager
from multiprocessing.pool import Pool
from multiprocessing.managers import SyncManager
from queue import Queue
from threading import Lock

from functools import partial

from tqdm import tqdm

from .atm_gate import ATMGate
from .atm_simulator import ATMSimulator

class ATMDetuneResponse:
    """
    Claculate and store the detuning response for a given ATM Pulse
    """

    def __init__(self, poolSize: int = 6) -> None:
        """
        Initalize class to default values
        """

        # Detunings to test the pulse against
        self.detunings: list[float] = []

        # Probability of flip corresponding to detuning
        self.probabilities: list[float] = []

        # Gate defining the pulse
        self.gate: ATMGate | None = None

        # Tolerance to define the range and sensitivity
        self.tolerance: float = 0.9

        # Sensitivity and range of the reponse
        self.sensitivity: float = -1
        self.range: float = -1

        # Bool to tell if the lists are currrently sorted properly
        self.sorted: bool = False

        # Multiprocessing Queue for the cpu bound task of calculating the reponse
        self.multiprocessingManager: SyncManager = Manager()
        self.detuningQueue: Queue[float] = self.multiprocessingManager.Queue()
        self.responseQueue: Queue[tuple[float, float]] = self.multiprocessingManager.Queue()
        self.calculationLock: Lock = self.multiprocessingManager.Lock()
        
        # Pool for calculating response
        self.poolSize: int = poolSize
        self.responsePool: Pool = Pool(poolSize)
        return


    def setATM(self, newGate: ATMGate) -> None:
        """
        Set ATM pusle to find response for
        """
        self.gate = newGate
        self.detunings = []
        self.probabilities = []
        return

    def compareATM(self, testGate: ATMGate) -> bool:

        if (self.gate is not None and
            self.gate.getTime() == testGate.getTime() and
            self.gate.riseTime == testGate.riseTime and
            self.gate.fallTime == testGate.fallTime and
            self.gate.maxAmplitude == testGate.maxAmplitude and
            self.gate.maxFrequency == testGate.maxFrequency and
            self.gate.riseGradient == testGate.riseGradient and
            self.gate.fallGradient == testGate.fallGradient):
            return True
        return False

    def setTolerance(self, newTolerance: float) -> None:
        """
        Set the tolerance to use when calculating sensitivity and range
        """
        self.tolerance = newTolerance
        return

    def testDetuning(
        self, 
        detuning: float | list[float] | None = None, 
        resolution: int = 200,
    ) -> float:
        """
        Test a given value or list of values of detunings
        """

        # Make sure a proper gate is bound
        if self.gate is None:
            raise TypeError("No Valid ATM Pulse currently set")

        # Get a list of values to test based on input
        testValues: list[float] = []
        if detuning is None:
            lowerBound = -self.gate.getMaxFrequency() * 1.25
            upperBound = self.gate.getMaxFrequency() * 1.25
            testValues = np.linspace(lowerBound ,upperBound ,resolution).tolist()
        elif isinstance(detuning, (float, int)):
            testValues.append(detuning)
        else:
            testValues = detuning

        if self.poolSize < 2:
            return ATMDetuneResponse._testSingleDetuning(self.gate, testValues[0])[1]

        atmFunc = partial(ATMDetuneResponse._testSingleDetuning, copy.deepcopy(self.gate))
        result = self.responsePool.map(atmFunc, testValues)
        for v in result:
            self.detunings.append(v[0])
            self.probabilities.append(v[1])

        # Return final probability calculated and mark list as unsorted
        self.sorted = False
        return self.probabilities[-1]

    @staticmethod
    def _testSingleDetuning(gate: ATMGate, testValue: float) -> tuple[float, float]:
        """
        Test a single detuning value
        """

        # atmCircuit = qst.QuantumCircuit(testValue)
        # atmCircuit.appendGate(gate)
        #
        # atmSimulator = qst.PulseSimulator()
        # atmSimulator.setCircuit(atmCircuit)
        #
        # simResolution = int(gate.getMaxFrequency() * gate.getTime() * 16)
        # atmResult = atmSimulator.simulateCircuit(simResolution, 2)

        simulator: ATMSimulator = ATMSimulator(gate, testValue)

        return (testValue, simulator.simulateCircuit())

    def testDetuningAsync(
        self,
        detuning: float | list[float] | None = None,
        resolution: int = 200,
    ) -> None:
        """
        Test a given value or list of values of detunings
        """

        # Make sure a proper gate is bound
        if self.gate is None:
            raise TypeError("No Valid ATM Pulse currently set")

        # Get a list of values to test based on input
        testValues: list[float] = []
        if detuning is None:
            lowerBound = -self.gate.getMaxFrequency() * 1.25
            upperBound = self.gate.getMaxFrequency() * 1.25
            testValues = np.linspace(lowerBound ,upperBound ,resolution).tolist()
        elif isinstance(detuning, (float, int)):
            testValues.append(detuning)
        else:
            testValues = detuning

        self.calculationLock.acquire()
        for val in testValues:
            self.detuningQueue.put(val)
        self.calculationLock.release()

        atmFunc = partial(ATMDetuneResponse._testSingleDetuningAsync, 
                          copy.deepcopy(self.gate),
                          self.responseQueue,
                          self.calculationLock)

        self.responsePool.map_async(atmFunc, testValues)
        return

    @staticmethod
    def _testSingleDetuningAsync(
        gate: ATMGate, 
        responseQueue: Queue[tuple[float, float]],
        calculationLock: Lock,
        testValue: float
    ) -> None:

        # atmCircuit = qst.QuantumCircuit(testValue)
        # atmCircuit.appendGate(gate)
        #
        # atmSimulator = qst.PulseSimulator()
        # atmSimulator.setCircuit(atmCircuit)
        #
        # simResolution = int(gate.getMaxFrequency() * gate.getTime() * 16)
        # atmResult = atmSimulator.simulateCircuit(simResolution, 2)

        simulator: ATMSimulator = ATMSimulator(gate, testValue)
        result = simulator.simulateCircuit()

        calculationLock.acquire()
        responseQueue.put((testValue, result))
        calculationLock.release()
        return

    def terminateAsync(self) -> None:
        self.responsePool.terminate()
        self.responsePool.join()
        return

    def _collectResponse(self) -> None:
        """
        Collect all calculated values for the ATM detuning response
        from the asynchronous calculation.
        """

        self.calculationLock.acquire()
        while not self.responseQueue.empty():
            front = self.responseQueue.get()
            self.detunings.append(front[0])
            self.probabilities.append(front[1])

        self.calculationLock.release()
        self.sorted=False
        return

    def getResponse(self) -> tuple[list[float], list[float], float, float]:
        """
        Get the detuning and respective flip probability for the currently calculated values
        """
        self._collectResponse()
        self._sortResponse()
        self.updateCharacteristics()
        return self.detunings, self.probabilities, self.sensitivity, self.range

    def updateCharacteristics(self) -> None:
        """
        Find the sensitivity and range for calculated response
        """
        self.findRange() 
        self.findSensitivity()
        return

    def findRange(self) -> None:
        """
        Find range for calculated response
        """
        if not self.sorted:
            self._sortResponse()

        self.range = -1
        prevProb = 0
        for det, prob in zip(self.detunings, self.probabilities):
            if prob < self.tolerance and prevProb > self.tolerance and det > 0 and det > self.range:
                self.range = 2 * det
            prevProb = prob
        return

    def findSensitivity(self) -> None:
        """
        Find sensitivity for calculated response
        """

        if not self.sorted:
            self._sortResponse()

        self.sensitivity = -1
        for det, prob in zip(self.detunings, self.probabilities):
            if prob > self.tolerance and det > 0:
                self.sensitivity = det * 2
                return
        return

    def _sortResponse(self) -> None:
        """
        Sort the probabilities and detunings in order of detunings
        """
        self.probabilities = [prob 
                              for _, prob 
                              in sorted(zip(self.detunings, self.probabilities))]
        self.detunings = sorted(self.detunings)
        self.sorted = True
        return

    def plotReponse(self, ax: matplotlib.axes.Axes) -> None:
        """
        Plot detuning response for the ATM pulse given a matplotlib axes
        """

        self._collectResponse()

        if len(self.detunings) == 0:
            return

        if not self.sorted:
            self._sortResponse()

        ax.plot(self.detunings, self.probabilities)
        ax.plot([-det for det in self.detunings], self.probabilities)
        ax.set_xlabel("Frequency (MHz)")
        ax.set_ylabel("Probability")
        ax.axhline(self.tolerance, alpha = 0.5, linestyle="--", label="Tolerance")
        ax.axhline(1, alpha = 0.5, linestyle="--")
        if self.sensitivity > 0:
            ax.axvline(self.sensitivity/2, 
                       alpha = 0.5, 
                       linestyle="--", 
                       label="Sens: {:.2f} kHz".format(self.sensitivity * 1e3))
        if self.range > 0:
            ax.axvline(self.range / 2, 
                       alpha = 0.5, 
                       linestyle="--", 
                       label="Range: {:.3f} MHz".format(self.range))
            ax.axvline(-self.range / 2, 
                       alpha = 0.5, 
                       linestyle="--", )
        ax.legend(loc="upper right")
        return


