import benchmark
from typing import List
import struct

class producerConsumer_5p2(benchmark.Benchmark):
    def __init__(self):
        self.__DIRECTORY__ = "5p2_producerConsumer"
        self.__TOP_ACTOR_NAME__ = "bndBuffer.BndBufferNetwork"
        self.__BENCHMARK_NAME__ = "producerConsumer"
        self.__XCLBIN_NAME__ = "BndBufferNetwork_kernel_xclbin"
        self.__TOP_ACTOR_NAME_NO_PREPATH__ = "BndBufferNetwork"
        self.__TOP_ACTOR_NAME_STREAMBLOCKS_SUFFIX__ = "Streamblocks"

    def getAMScalingParameters(self) -> List[tuple]:
        parameters = [
            #("P", [1, 2, 3]), # Best for testing
            #("C", [1]),
            #("P", [16,18,20,22,24,26]), # Best for testing
            ("P", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 24, 26, 28, 30, 35, 40, 45, 50, 55, 60, 70, 80, 90, 100]), # Best for unreduced state machine measurements
            ("C", [1]),
            #("P", [1, 2, 3, 4, 5, 6, 7]), # Best for runtimes
            #("C", [1, 2, 3, 4 ,5, 6, 7]),
        ]
        return parameters

    def getBuildParameters(self) -> List[tuple]:
        parameters = self.getAMScalingParameters()
        parameters = parameters + [
            ("nItems", [1000000]) # The number of tokens each producer sends
        ]
        return parameters

    def getConfigFileContents(self, **kwargs) -> str:
        P = kwargs["P"]
        C = kwargs["C"]
        B = kwargs["B"] if "B" in kwargs else 50
        nItems = kwargs["nItems"]

        configFileContents = f"""namespace bndBuffer:
    uint B = {B}; // Buffer size
    uint P = {P}; // Number of producers
    uint C = {C}; // Number of consumers
    uint numItemsPerProducer = {nItems};
    uint prodCost = 1; // Cost to perform action by producer
    uint consCost = 1; // Cost to perform action by consumer
end
"""
        return configFileContents

    def confirmRuntime(self, **kwargs) -> bool:
        P = kwargs["P"]
        C = kwargs["C"]
        nItems = kwargs["nItems"]

        with open(self.__DIRECTORY__ + "/data/out", mode="rb") as file:
            fileContent = file.read()
            checksum = struct.unpack("II", fileContent)
            if checksum[0] != P*nItems or checksum[1] != P*nItems:
                raise Exception(
                    f"P={P}, C={C}. Checksum value: {checksum[0]}, {checksum[1]}, expected {P*nItems} for both."
                )

        return True

    def getInputFiles(self) -> List[str]:
        return []

    def getOutputFiles(self) -> List[str]:
        retList = ["out"]
        retList = [self.__DIRECTORY__ + "/data/" + s for s in retList]
        return retList

    def getDependentVariableKey(self) -> str:
        return "P"
    
    def getScalingActorName(self) -> str:
        return "Buffer"
    
