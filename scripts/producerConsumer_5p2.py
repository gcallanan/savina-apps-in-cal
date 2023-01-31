import benchmark
from typing import List

class producerConsumer_5p2(benchmark.Benchmark):
    def __init__(self):
        self.__DIRECTORY__ = "5p2_producerConsumer"
        self.__TOP_ACTOR_NAME__ = "bndBuffer.BndBufferNetwork"
        self.__BENCHMARK_NAME__ = "producerConusmer"

    def getAMScalingParameters(self) -> List[tuple]:
        parameters = [
            #("P", [1, 2]), # Best for testing
            #("C", [1, 2]),
            ("P", [1, 2, 3, 4]), # Best for unreduced state machine measurements
            ("C", [1, 2, 3, 4]),
            #("P", [1, 2, 3, 4, 5, 6, 7]), # Best for runtimes
            #("C", [1, 2, 3, 4 ,5, 6, 7]),
        ]
        return parameters

    def getBuildParameters(self) -> List[tuple]:
        parameters = self.getAMScalingParameters()
        parameters = parameters + []
        return parameters

    def getConfigFileContents(self, **kwargs) -> str:
        P = kwargs["P"]
        C = kwargs["C"]
        B = kwargs["B"] if "B" in kwargs else 50

        configFileContents = f"""namespace bndBuffer:
    uint B = {B}; // Buffer size
    uint P = {P}; // Number of producers
    uint C = {C}; // Number of consumers
    uint numItemsPerProducer = 1000;
    uint prodCost = 25; // Cost to perform action by producer
    uint consCost = 25; // Cost to perform action by consumer
end
"""
        return configFileContents

    def confirmRuntime(self, **kwargs) -> bool:
        # Dont really have a check for this test. Just hope that it works.
        # Thats a viable strategy right?
        return True

    def getInputFiles(self) -> List[str]:
        return []

    def getOutputFiles(self) -> List[str]:
        return []

    def getDependentVariableKey(self) -> str:
        return "P"