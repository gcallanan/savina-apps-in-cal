import time
import utilities
import subprocess
from benchmark import Benchmark

from typing import List
from copy import deepcopy
from big_4p8 import big_4p8
from trapezoid_6p12 import trapezoid_6p12
from producerConsumer_5p2 import producerConsumer_5p2

"""
Generate a list of individual experiments from all combinations of the parameters in the input list
Eg: 
    [
        ("W", [1, 5])
        ("N", [10000, 20000])
    ]

Transforms to:
    [
        {W=1, N=10000},
        {W=1, N=10000},
        {W=5, N=20000},
        {W=5, N=20000},
    ]
"""
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


"""
Run all experiments where the runtime of the actor network is recorded. These experiments
parameters are determined based on the benchmark.getBuildParameters() function.

The output for these results are stored in:
    <benchmark directory>/statistics/runtimes.csv
"""
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


"""
Run all experiments where the compile time of the actor network is recorded. These experiments
parameters are determined based on the benchmark.getAMScalingParameters function.

Results that are recorded for each experiment include:
    1. Time taken to run each compiler phase (stored in <benchmark directory>/statistics/compilePhaseTimes.csv)
    2. Size of the actor machines for each actor after the AM reduction has been performed (stored
       in <benchmark directory>/statistics/amSizeStatistics_postAmReduction.csv)
    3. Size of the actor machines for each actor before AM reduction has been perfomed. stored
       in <benchmark directory>/statistics/amSizeStatistics_postAndPreAmReduction.csv Note: the
       sizes after the reduction are also included here to make comparisons easier) 

@param collectPreReductionStats Experiment 3 above can take a very long time to run with a risk of
                                crashing. Set this flag to false to prevent running this test and 
                                speed up testing by orders of magnitude.
"""
def runCompilationExperiments(benchmark: Benchmark, collectPreReductionStats = False):
    experimentParams = generateExperimentParams(benchmark.getAMScalingParameters())
    testIndex = 0
    compilerExperimentResults = []
    numTests = len(experimentParams)

    # 1. Standard compilation experiments collecting phase timing and 

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
            benchmark.__TOP_ACTOR_NAME__, benchmark.__DIRECTORY__, am_statistics_post_reduction=True
        )

        compilerExperimentResults.append(
            utilities.CompileTimeExperimentResults(
                experimentParam, compileTime_s, compilerPhaseOutput, compilerAmOutput, False
            )
        )
        testIndex += 1

    utilities.writeConfigFile(
        benchmark, experimentParams[0]
    )  # reset to prevent git commit issues

    runningTime_s = round(time.time() - startTime_s, 2)
    print(f"{runningTime_s:07.2f} Done running compile tests for {benchmark.__TOP_ACTOR_NAME__}.")

    utilities.writeCompilerPhaseFiles(benchmark.__DIRECTORY__, compilerExperimentResults)
    utilities.writeAmStatisticsResults(benchmark.__DIRECTORY__, compilerExperimentResults, "postAmReduction")

    

    if(collectPreReductionStats):
        timeout_s = compilerExperimentResults[-1].compileTime_s*10 if compilerExperimentResults[-1].compileTime_s*10 > 900 else 900
        # 2. Collect stats pre-am reduction
        testIndex = 0
        for experimentParam in experimentParams:
            runningTime_s = round(time.time() - startTime_s, 2)

            utilities.writeConfigFile(benchmark, experimentParam)

            print(
                f"{runningTime_s:07.2f} Running pre-reduction AM statistics collection test {testIndex+1} of {numTests} for {benchmark.__TOP_ACTOR_NAME__} with params:",
                experimentParam,
            )

            try:
                compilerAmOutput, compileTime_s = utilities.buildActor(
                    benchmark.__TOP_ACTOR_NAME__, benchmark.__DIRECTORY__, am_statistics_pre_reduction=True, timeout_s=timeout_s
                )
            except subprocess.TimeoutExpired:
                print("Timeout:", timeout_s, "s")
                break
            except RuntimeError:
                print("Runtime error on collect stats pre-am reduction")
                break


            compilerExperimentResults.append(
                utilities.CompileTimeExperimentResults(
                    experimentParam, compileTime_s, "", compilerAmOutput, True
                )
            )
            testIndex += 1

        utilities.writeConfigFile(
            benchmark, experimentParams[0]
        )  # reset to prevent git commit issues

        runningTime_s = round(time.time() - startTime_s, 2)
        print(f"{runningTime_s:07.2f} Done running pre-reduction AM statistics collection tests for {benchmark.__TOP_ACTOR_NAME__}.")

        utilities.writeAmStatisticsResults(benchmark.__DIRECTORY__, compilerExperimentResults, "postAndPreAmReduction")

# Main function that runs all tests for the different benchmarks included in the benchmarks array below
if __name__ == "__main__":
    benchmarks = [producerConsumer_5p2()]#[big_4p8(), trapezoid_6p12()]

    index = 1
    start = time.time()
    for benchmark in benchmarks:
        runningTime_s = time.time() - start
        print(
            f"{runningTime_s:07.2f} Running {benchmark.__BENCHMARK_NAME__}. This is benchmark {index} of {len(benchmarks)}"
        )
        print("Running runtime experiments:")
        runRuntimeExperiments(benchmark)
        print("Running compiler experiments:")
        runCompilationExperiments(benchmark, collectPreReductionStats=True)

        index += 1

    print()
    print("Done!")
