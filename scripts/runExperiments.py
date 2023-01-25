import time
import utilities
from benchmark import Benchmark

from typing import List
from copy import deepcopy
from big_4p8 import big_4p8


def generateExperimentParams(params: List[tuple]) -> List[dict]:
    paramsCopy = deepcopy(params)
    output = []

    while len(paramsCopy) != 0:
        row = paramsCopy.pop()
        key = row[0]
        values = row[1]

        newOutput = []
        for x in values:
            if len(output) == 0:
                newOutput.append({key: x})
            else:
                for item in output:
                    newItem = dict(item)
                    newItem[key] = x
                    newOutput.append(newItem)
        output = newOutput

    return output


# 1. Run timing experiements
def runRuntimeExperiments(benchmark: Benchmark):
    experimentParams = generateExperimentParams(benchmark.getBuildParameters())
    testIndex = 0
    runtimeExperimentResults = []
    numTests = len(experimentParams)

    startTime_s = time.time()

    utilities.makeDataDir(benchmark)
    for experimentParam in experimentParams:
        runningTime_s = round(time.time() - startTime_s, 2)
        print(
            f"{runningTime_s:07.2f} Running runtime test {testIndex+1} of {numTests} for {benchmark.__TOP_ACTOR_NAME__} with params:",
            experimentParam,
        )

        utilities.writeConfigFile(benchmark, experimentParam)
        utilities.buildActor(
            benchmark.__TOP_ACTOR_NAME__, benchmark.__DIRECTORY__, phase_timers=True
        )
        runTime_s = utilities.runActor(
            benchmark.__DIRECTORY__,
            benchmark.getInputFiles(),
            benchmark.getOutputFiles(),
        )
        if not benchmark.confirmRuntime(**experimentParam):
            raise Exception(experimentParam + " did not return the correct value.")

        runtimeExperimentResults.append(
            utilities.RuntimeExperimentResults(experimentParam, runTime_s)
        )
        testIndex += 1

    utilities.writeConfigFile(
        benchmark, experimentParams[0]
    )  # reset to prevent git commit issues

    utilities.writeRuntimeFiles(
        benchmark.__DIRECTORY__,
        runtimeExperimentResults,
        benchmark.getDependentVariableKey(),
    )


# 2. Run compilation experiments
def runCompilationExperiments(benchmark: Benchmark):
    experimentParams = generateExperimentParams(benchmark.getAMScalingParameters())
    testIndex = 0
    compilerExperimentResults = []
    numTests = len(experimentParams)

    startTime_s = time.time()

    utilities.makeDataDir(benchmark)
    for experimentParam in experimentParams:
        runningTime_s = round(time.time() - startTime_s, 2)
        print(
            f"{runningTime_s:07.2f} Running compile test {testIndex+1} of {numTests} for {benchmark.__TOP_ACTOR_NAME__} with params:",
            experimentParam,
        )

        utilities.writeConfigFile(benchmark, experimentParam)
        compilerPhaseOutput, compileTime_s = utilities.buildActor(
            benchmark.__TOP_ACTOR_NAME__, benchmark.__DIRECTORY__, phase_timers=True
        )
        compilerAmOutput, compileTime_s = utilities.buildActor(
            benchmark.__TOP_ACTOR_NAME__, benchmark.__DIRECTORY__, am_statistics=True
        )

        compilerExperimentResults.append(
            utilities.CompileTimeExperimentResults(
                experimentParam, compileTime_s, compilerPhaseOutput, compilerAmOutput
            )
        )
        testIndex += 1

    utilities.writeConfigFile(
        benchmark, experimentParams[0]
    )  # reset to prevent git commit issues

    utilities.writeCompilerFiles(benchmark.__DIRECTORY__, compilerExperimentResults)


if __name__ == "__main__":
    benchmarks = [big_4p8(), big_4p8()]

    index = 1
    start = time.time()
    for benchmark in benchmarks:
        runningTime_s = time.time() - start
        print(
            f"{runningTime_s:07.2f} Running {benchmark.__BENCHMARK_NAME__}. This is benchmark {index} of {len(benchmarks)}"
        )
        print("Running runtime experiments:")
        runRuntimeExperiments(benchmark)
        print("Running compiletime experiments:")
        runCompilationExperiments(benchmark)

        index += 1

    print()
    print("Done!")