from abc import ABC, abstractmethod
from typing import List

#NOTE: Some inconsistencies between how we generate different experiment parameters, could be fixed

class Benchmark(ABC):
    def __init__(self):
        self.__BENCHMARK_NAME__ = ""
        self.__DIRECTORY__ = ""
        self.__TOP_ACTOR_NAME__ = ""
        self.__XCLBIN_NAME__ = ""
        self.__TOP_ACTOR_NAME_NO_PREPATH__ = ""
        self.__TOP_ACTOR_NAME_STREAMBLOCKS_SUFFIX__ = ""

    @abstractmethod
    def getAMScalingParameters(self) -> List[tuple]:
        '''
        These parameters are any parameters that affect the size of the Actor/AM at compile time.
        Each parameter must include all possible values that need to be tested.

        For example, if an actor has Pin and Pout ports and we want to test a range of these
        ports, then the entry should be:

        parameters = [
            ("Pin", [2, 3, 4, 5, 6]),
            ("Pout", [2, 3, 4, 5, 6])
        ]

        '''
        pass

    @abstractmethod
    def getBuildParameters(self) -> List[tuple]:
        '''
        These are all parameters that affect how the actor performs and scales. The AM scaling parameters need
        to be inserted into these build parameters.

        Each parameter must include all possible values that need to be tested.

        For example if an actor must send N messages, then the actor size does not change.
        The entry could look like this:

        parameters = self.getAMScalingParameters() + [
            ("N", [100, 200, 300])
        ]

        '''
        pass

    def getAMScalingExperimentParameters(self) -> List[tuple]:
        """
        This is for when you want to run experiments only to test the actor scaling, but you still need the build parameters to compile.

        The different values of build parameters are reduced to 1. For example if getBuildParameters() produces

        parameters = [
            ("Pin", [2, 3, 4, 5, 6]),
            ("Pout", [2, 3, 4, 5, 6]),
            ("N", [100, 200, 300])
        ]

        but only Pin and Pout are scaling values, then this function produces:
        parameters = [
            ("Pin", [2, 3, 4, 5, 6]),
            ("Pout", [2, 3, 4, 5, 6]),
            ("N", [100])
        ]
        """
        allParamsList = self.getBuildParameters()
        scalingParamsList = self.getAMScalingParameters()
        output = self.getAMScalingParameters()
        for param, value in allParamsList:
            if(param not in list(zip(*scalingParamsList))[0]): # Check if the param is not in AMScalingParameters
                output = output + [(param, [value[0]])]

        return output


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
