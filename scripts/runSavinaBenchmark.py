"""
File that runs all the savina benchmarks with all the parameters given in the implementation of the
benchmark.Benchmark class.

Both compile time and runtime tests are run
"""

import time
import string
import utilities
import subprocess
import argparse

from typing import List

# Import all the benchmarks
from benchmark import Benchmark
from big_4p8 import big_4p8
from trapezoid_6p12 import trapezoid_6p12
from producerConsumer_5p2 import producerConsumer_5p2
from threadRing_4p2 import threadRing_4p2

"""
Run all experiments where the runtime of the actor network is recorded. These experiments
parameters are determined based on the benchmark.getBuildParameters() function.

The output for these results are stored in:
    <benchmark directory>/statistics/runtimes_*.csv
"""
def runRuntimeExperiments(
        benchmark: Benchmark,
        reduction_algorithm: string = "informative-tests", #<(first | random | shortest-path-to-exec | informative-tests | informative-tests-if-true | informative-tests-if-false | ordered-condition-checking)>)
    ):
    experimentParams = utilities.generateExperimentParams(benchmark.getBuildParameters())
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
        try:
            utilities.buildActor(
                benchmark.__TOP_ACTOR_NAME__, benchmark.__DIRECTORY__, phase_timers=True, reduction_algorithm=reduction_algorithm, timeout_s=600,
            )
        except RuntimeError:
                raise RuntimeError("Runtime error on collect stats pre-am reduction")
        except subprocess.TimeoutExpired:
                raise RuntimeError("Timeout:", 600, "s")
                break
        
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
        reduction_algorithm,
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

The output for these results are stored in:
    <benchmark directory>/statistics/amSizeStatistics_*.csv
    <benchmark directory>/statistics/compilePhaseTimes_*.csv
"""
def runCompilationExperiments(
        benchmark: Benchmark, 
        collectPreReductionStats = False,
        reduction_algorithm: string = "informative-tests",
        firstExperimentIndex: int = 0, # Experiment will be repeated lastExperimentIndex - firstExperimentIndex times with each output file getting an index between firstExperimentIndex and lastExperimentIndex.
        lastExperimentIndex: int = 0,
    ):
    
    for i in range(firstExperimentIndex,lastExperimentIndex + 1):
        print("Test: ",i)
        experimentParams = utilities.generateExperimentParams(benchmark.getAMScalingParameters())
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
            try:
                compilerPhaseOutput, compileTime_s, binSize_bytes = utilities.buildActor(
                    benchmark.__TOP_ACTOR_NAME__, benchmark.__DIRECTORY__, phase_timers=True, reduction_algorithm=reduction_algorithm, timeout_s=600, compile_C_to_binary=False
                )
                compilerAmOutput, compileTime_s, binSize_bytes = utilities.buildActor(
                    benchmark.__TOP_ACTOR_NAME__, benchmark.__DIRECTORY__, am_statistics_post_reduction=True, reduction_algorithm=reduction_algorithm, timeout_s=600, compile_C_to_binary=False
                )
            except subprocess.TimeoutExpired:
                print("Timeout:", timeout_s, "s")
                break
            except RuntimeError:
                print("Runtime error")
                break


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

        utilities.writeCompilerPhaseFiles(benchmark.__DIRECTORY__, compilerExperimentResults, reduction_algorithm,f"{i}")
        utilities.writeAmStatisticsResults(benchmark.__DIRECTORY__, compilerExperimentResults, f"postAmReduction{i}", reduction_algorithm)

    

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
                    benchmark.__TOP_ACTOR_NAME__, benchmark.__DIRECTORY__, am_statistics_pre_reduction=True, timeout_s=timeout_s,
                )
            except subprocess.TimeoutExpired:
                print("Timeout:", timeout_s, "s")
                break
            except RuntimeError:
                print("Runtime error on collect stats pre-am reduction")
                break

            compilerExperimentResults.append(
                utilities.CompileTimeExperimentResults(
                    experimentParam, compileTime_s, "", compilerAmOutput, True, reduction_algorithm
                )
            )
            testIndex += 1

        utilities.writeConfigFile(
            benchmark, experimentParams[0],
        )  # reset to prevent git commit issues

        runningTime_s = round(time.time() - startTime_s, 2)
        print(f"{runningTime_s:07.2f} Done running pre-reduction AM statistics collection tests for {benchmark.__TOP_ACTOR_NAME__}.")

        utilities.writeAmStatisticsResults(benchmark.__DIRECTORY__, compilerExperimentResults, f"postAndPreAmReduction", reduction_algorithm)

# Main function that runs all tests for the different benchmarks included in the benchmarks array below
if __name__ == "__main__":
    # 1. List of different benchmarks to run
    benchmarks = [threadRing_4p2(), big_4p8(), producerConsumer_5p2(), trapezoid_6p12()]
    #benchmarks = [producerConsumer_5p2()]

    # 2. Parse all arguments
    parser = argparse.ArgumentParser(description='Run Savina Benchmark suite for CAL.')
    parser.add_argument('--pre-stats', action='store_true', help="Collect AM statistics pre reduction (Greatly increases program runtime.)")
    parser.add_argument('--reduction-algorithm',
            default='informative-tests',
            const='informative-tests',
            nargs='?',
            choices=utilities.getReductionAlgorithms(),
            help='Choose which reduction algorithm to use to reduce the Actor Machines (default: %(default)s)'
        )
    args = parser.parse_args()

    # 3. Run benchmarks
    print(f"Running benchmark test. Using reduction algorithm: {args.reduction_algorithm}. Pre-reduction stats printing: {args.pre_stats}")

    index = 1
    start = time.time()
    for benchmark in benchmarks:
        runningTime_s = time.time() - start
        print(
            f"{runningTime_s:07.2f} Running {benchmark.__BENCHMARK_NAME__}. This is benchmark {index} of {len(benchmarks)}"
        )
        print("Running runtime experiments:")
        runRuntimeExperiments(benchmark, reduction_algorithm=args.reduction_algorithm)
        print("Running compiler experiments:")
        runCompilationExperiments(benchmark, collectPreReductionStats=args.pre_stats, reduction_algorithm=args.reduction_algorithm)

        index += 1

    print()
    print("Done!")
