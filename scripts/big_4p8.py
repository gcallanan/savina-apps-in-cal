import benchmark
from typing import List
import struct


class big_4p8(benchmark.Benchmark):
    def __init__(self):
        self.__DIRECTORY__ = "4p8_big"
        self.__TOP_ACTOR_NAME__ = "big.BigNetwork"
        self.__BENCHMARK_NAME__ = "big"

    def getAMScalingParameters(self) -> List[tuple]:
        parameters = [
            ("N", [2, 3, 4, 5, 6]),
        ]
        return parameters

    def getBuildParameters(self) -> List[tuple]:
        parameters = self.getAMScalingParameters()

        parameters = parameters + [
            ("P", [1000, 10000, 100000, 1000000, 10000000]),
        ]
        return parameters

    def getConfigFileContents(self, **kwargs) -> str:
        N = kwargs["N"]
        P = kwargs["P"] if "P" in kwargs else 1000

        configFileContents = f"""namespace big:
    uint numMessengers = {N};
    uint numPingPongs = {P};
end
"""
        return configFileContents

    # Need something to confirm correctness
    def confirmRuntime(self, **kwargs) -> bool:
        N = kwargs["N"]
        P = kwargs["P"]

        with open(self.__DIRECTORY__ + "/data/out", mode="rb") as file:
            fileContent = file.read()
            checksum = struct.unpack("i", fileContent)
            if checksum[0] != N:
                raise Exception(
                    f"N={N}, P={P}. Checksum value: {checksum[0]}, expected {N}"
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
