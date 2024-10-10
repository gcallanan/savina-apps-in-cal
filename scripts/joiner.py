import benchmark
from typing import List
import struct


class joiner(benchmark.Benchmark):
    def __init__(self):
        self.__DIRECTORY__ = "joiner"
        self.__TOP_ACTOR_NAME__ = "joiner.Top"
        self.__BENCHMARK_NAME__ = "Joiner"
        self.__XCLBIN_NAME__ = "Joiner_kernel_xclbin"
        self.__TOP_ACTOR_NAME_NO_PREPATH__ = "Top"

    def getAMScalingParameters(self) -> List[tuple]:
        parameters = [
            #("W", [1, 5, 10, 20, 30, 40, 50]),
            ("K", list(range(5,1001,5))),
        ]
        return parameters

    def getBuildParameters(self) -> List[tuple]:
        parameters = self.getAMScalingParameters()
        parameters = parameters + []
        return parameters

    def getConfigFileContents(self, **kwargs) -> str:
        K = kwargs["K"] if "K" in kwargs else 100

        configFileContents = f"""namespace joiner:
    uint K = {K}; // Number of inputs
end
"""
        return configFileContents

    # Need something to confirm correctness
    def confirmRuntime(self, **kwargs) -> bool:
        K = kwargs["K"]

        with open(self.__DIRECTORY__ + "/data/out", mode="rb") as file:
            for i in range(0,K):
                fileContent = file.read(4)
                checksum = struct.unpack("<I", fileContent)
                
                if checksum[0] != i:
                    raise Exception(
                        f"K={K}, Checksum value: {checksum} at index {i}, expected {i} for both."
                    ) 

        return True

    def getInputFiles(self) -> List[str]:
        return []

    def getOutputFiles(self, experimentParams) -> List[str]:
        retList = ["out"]
        retList = [self.__DIRECTORY__ + "/data/" + s for s in retList]
        return retList

    def getDependentVariableKey(self) -> str:
        return "K"
    
    def getScalingActorName(self) -> str:
        return "Joiner"
