import benchmark
from typing import List


class threadRing_4p2(benchmark.Benchmark):
    def __init__(self):
        self.__DIRECTORY__ = "4p2_threadRing"
        self.__TOP_ACTOR_NAME__ = "threadRing.ThreadRing"
        self.__BENCHMARK_NAME__ = "ThreadRing"
        self.__XCLBIN_NAME__ = "ThreadRing_kernel_xclbin"
        self.__TOP_ACTOR_NAME_NO_PREPATH__ = "ThreadRing"

    def getAMScalingParameters(self) -> List[tuple]:
        parameters = [
            #("W", [1, 5, 10, 20, 30, 40, 50]),
            ("N", list(range(25,1001,25))),
        ]
        return parameters

    def getBuildParameters(self) -> List[tuple]:
        parameters = self.getAMScalingParameters()
        parameters = parameters + []
        return parameters

    def getConfigFileContents(self, **kwargs) -> str:
        N = kwargs["N"] if "N" in kwargs else 100

        configFileContents = f"""namespace threadRing:
    uint N = {N}; // Number of actors
    uint R = 100000; // Number of pings
end
"""
        return configFileContents

    # Need something to confirm correctness
    def confirmRuntime(self, **kwargs) -> bool:
        #Would be nice to have something here *man shrugging emoji*    

        return True

    def getInputFiles(self) -> List[str]:
        return []

    def getOutputFiles(self) -> List[str]:
        return []

    def getDependentVariableKey(self) -> str:
        return "N"
    
    def getScalingActorName(self) -> str:
        return "ThreadRingActor"
