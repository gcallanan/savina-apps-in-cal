import benchmark
from typing import List
import struct


class big_4p8(benchmark.Benchmark):
    def __init__(self):
        self.__DIRECTORY__ = "4p8_big"
        self.__TOP_ACTOR_NAME__ = "big.BigNetwork"
        self.__BENCHMARK_NAME__ = "big"
        self.__XCLBIN_NAME__ = "BigNetworkStreamblocks_kernel_xclbin"
        self.__TOP_ACTOR_NAME_NO_PREPATH__ = "BigNetwork"
        self.__TOP_ACTOR_NAME_STREAMBLOCKS_SUFFIX__ = "Streamblocks"

    def getAMScalingParameters(self) -> List[tuple]:
        parameters = [
            ("N", [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 ,13 ,14, 15, 16, 17, 18, 19, 20, 22, 24, 26, 28, 30, 35, 40, 45, 50, 55, 60]),
            # ("N", [2, 3, 4, 5, 6]),
            #("N", [2, 3]),
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
    
    def getScalingActorName(self) -> str:
        return "Messenger"
