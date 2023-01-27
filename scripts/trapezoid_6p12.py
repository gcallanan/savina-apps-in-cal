import benchmark
from typing import List
import struct


class trapezoid_6p12(benchmark.Benchmark):
    def __init__(self):
        self.__DIRECTORY__ = "6p12_trapezoid"
        self.__TOP_ACTOR_NAME__ = "trapezoid.TrapezoidNetwork"
        self.__BENCHMARK_NAME__ = "trapezoid"

    def getAMScalingParameters(self) -> List[tuple]:
        parameters = [
            ("W", [1, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]),
        ]
        return parameters

    def getBuildParameters(self) -> List[tuple]:
        parameters = self.getAMScalingParameters()

        parameters = parameters + [
            ("N", [1000, 10000, 100000]),
        ]
        return parameters

    def getConfigFileContents(self, **kwargs) -> str:
        W = kwargs["W"]
        N = kwargs["N"] if "N" in kwargs else 1000

        configFileContents = f"""namespace trapezoid:
    int N = {N}; // num pieces (in total, each worker gets N/W pieces)
    int W = {W}; // num workers
    float L = 1; // left end-point
    float R = 5; // right end-point
end
"""
        return configFileContents

    # Need something to confirm correctness
    def confirmRuntime(self, **kwargs) -> bool:
        # N = kwargs["N"]
        # P = kwargs["P"]
        #
        # with open(self.__DIRECTORY__ + "/data/out", mode="rb") as file:
        #     fileContent = file.read()
        #     checksum = struct.unpack("i", fileContent)
        #     if checksum[0] != N:
        #         raise Exception(
        #             f"N={N}, P={P}. Checksum value: {checksum[0]}, expected {N}"
        #         )

        return True

    def getInputFiles(self) -> List[str]:
        return []

    def getOutputFiles(self) -> List[str]:
        retList = ["out"]
        retList = [self.__DIRECTORY__ + "/data/" + s for s in retList]
        return retList

    def getDependentVariableKey(self) -> str:
        return "N"
