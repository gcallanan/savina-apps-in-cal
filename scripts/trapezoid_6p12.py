import benchmark
from typing import List
import struct


class trapezoid_6p12(benchmark.Benchmark):
    def __init__(self):
        self.__DIRECTORY__ = "6p12_trapezoid"
        self.__TOP_ACTOR_NAME__ = "trapezoid.TrapezoidNetwork"
        self.__BENCHMARK_NAME__ = "trapezoid"
        self.__XCLBIN_NAME__ = "TrapezoidNetwork_kernel_xclbin"

    def getAMScalingParameters(self) -> List[tuple]:
        parameters = [
            #("W", [1, 5, 10, 20, 30, 40, 50]),
            ("W", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 30, 40, 50]),
            #("W", [1]),
        ]
        return parameters

    def getBuildParameters(self) -> List[tuple]:
        parameters = self.getAMScalingParameters()

        parameters = parameters + [
            #("N", [10000]),
            ("N", [10000, 20000, 40000, 70000, 100000]),
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
        N = kwargs["N"]
        W = kwargs["W"]
        
        with open(self.__DIRECTORY__ + "/data/out", mode="rb") as file:
            fileContent = file.read()
            checksum = struct.unpack("f", fileContent)
            if checksum[0] < 0.271078 or checksum[0] > 0.271082 :
                raise Exception(
                    f"W={W}, N={N}. Checksum value: {checksum[0]}, expected between 0.271079 and 0.271081"
                )

        return True

    def getInputFiles(self) -> List[str]:
        return []

    def getOutputFiles(self) -> List[str]:
        retList = ["out"]
        retList = [self.__DIRECTORY__ + "/data/" + s for s in retList]
        return retList

    def getDependentVariableKey(self) -> str:
        return "N"
    
    def getScalingActorName(self) -> str:
        return "Coordinator"
