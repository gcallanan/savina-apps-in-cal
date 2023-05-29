from abc import ABC, abstractmethod
from typing import List


class Benchmark(ABC):
    def __init__(self):
        self.__BENCHMARK_NAME__ = ""
        self.__DIRECTORY__ = ""
        self.__TOP_ACTOR_NAME__ = ""
        self.__XCLBIN_NAME__ = ""
        self.__TOP_ACTOR_NAME_NO_PREPATH__ = ""

    @abstractmethod
    def getAMScalingParameters(self) -> List[tuple]:
        pass

    @abstractmethod
    def getBuildParameters(self) -> List[tuple]:
        pass

    @abstractmethod
    def getConfigFileContents(self, **kwargs) -> str:
        pass

    @abstractmethod
    def confirmRuntime(self, **kwargs) -> bool:
        pass

    @abstractmethod
    def getInputFiles(self) -> List[str]:
        pass

    @abstractmethod
    def getOutputFiles(self) -> List[str]:
        pass

    @abstractmethod
    def getDependentVariableKey(self) -> str:
        pass

    @abstractmethod
    def getScalingActorName(self) -> str:
        pass

    # @property
    # @abstractmethod
    # def __DIRECTORY__(self):
    #    pass
