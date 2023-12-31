"""
@author Gareth Callanan

Script that tests how much the AM size impacts program performance performance compared to the C compiler optimisation flags.
"""

import csv
import utilities
import benchmark

from threadRing_4p2 import threadRing_4p2
from big_4p8_v1 import big_4p8_v1
from big_4p8_v2 import big_4p8_v2
from producerConsumer_5p2 import producerConsumer_5p2
from trapezoid_6p12 import trapezoid_6p12


def runAmVsOptimisationTests(benchmark: benchmark.Benchmark):
    print("Test:",benchmark.__BENCHMARK_NAME__)

    # 1. Get the parameters for the different experiments and then select the last experiment
    # in the list as this is the one that typically is the largest
    experimentParams = utilities.generateExperimentParams(benchmark.getBuildParameters())
    experIndex = -1
    lastExperiment = experimentParams[experIndex]
    firstExperiment = experimentParams[0]

    # 2. Set up outputRuntime and outputBinarySize arrays that will be written to CSV file
    reductionAlgorithms = ["first", "ordered-condition-checking" ,"informative-tests"]
    compilerFlags = ["-O0", "-O1", "-O2", "-O3"]
    print(lastExperiment)

    
    outputRuntime = [[benchmark.__BENCHMARK_NAME__ + ": Runtime"] + ['']*len(compilerFlags)]
    outputRuntime.append([str(lastExperiment)] + ['']*len(compilerFlags))
    outputRuntime.append([f'Scaling Actor: {benchmark.getScalingActorName()}'] + ['']*len(compilerFlags))
    outputRuntime.append([''] + compilerFlags)

    outputBinarySize = [[benchmark.__BENCHMARK_NAME__ + ": Binary Size (KB)" ] + ['']*len(compilerFlags)]
    outputBinarySize.append([str(lastExperiment)] + ['']*len(compilerFlags))
    outputBinarySize.append([''] + compilerFlags)

    # 3. Run the benchmarks for different optimisation flags and reduction algorithms
    for algorithm in reductionAlgorithms:
        outputLineRuntime = [algorithm]
        outputLineBinarySize = [algorithm]
        print(algorithm)
        for flag in compilerFlags:
            # 3.1. Write the config file with the last experiment
            utilities.writeConfigFile(benchmark, lastExperiment)


            printStats = False
            # This is a specific issue that occurs when trying to run producer/consumer benchmark with P > 10. Counting the states causes the program to crash. So we skip this when generating results
            if(not (algorithm == "informative-tests" and experIndex >= 10 and benchmark.__BENCHMARK_NAME__ == "producerConsumer")):
                printStats = True

            # 3.2. Compile the benchmark
            compilerPhaseOutput, compileTime_s, binarySize_bytes = utilities.buildActor(
                            benchmark.__TOP_ACTOR_NAME__, 
                            benchmark.__DIRECTORY__, 
                            am_statistics_post_reduction=printStats,
                            phase_timers=False, 
                            reduction_algorithm=algorithm,
                            extra_c_compiler_flags=flag
                        )
            
            # 3.3. Run the benchmark
            runTime_s = utilities.runActor(
                        benchmark.__DIRECTORY__,
                        benchmark.getInputFiles(),
                        benchmark.getOutputFiles(),
                    )
            
            # 3.4. Get the number of states in the actor that scales - we dont need to run
            # this every loop iteration but I am too lazy to change it
            if(printStats):
                numStates = 0
                for line in compilerPhaseOutput.splitlines():
                    if benchmark.getScalingActorName() in line:
                        print(algorithm ,flag, runTime_s, line)
                        numStates = line.split(",")[1]
                        break
            else:
                numStates = 83
                print(algorithm ,flag, runTime_s)

            # 3.5. Write the runtime to single line
            outputLineRuntime.append(round(runTime_s,6))
            outputLineBinarySize.append(round(binarySize_bytes/1024,2))

        # 3.6. Write the single lines to the arrays that eventually become CSV files
        outputLineRuntime[0] += f" (states: {numStates})"
        outputRuntime.append(outputLineRuntime)
        outputBinarySize.append(outputLineBinarySize)

    # 4. Reset config file so we dont have it requiring constant git commits.
    utilities.writeConfigFile(benchmark, firstExperiment)

    # 5. Print out results and write results to file

    # 5.1. Print runtimes
    # Taken straight from stackoverflow: https://stackoverflow.com/questions/13214809/pretty-print-2d-list    
    print("")
    s1 = [[str(e) for e in row] for row in outputRuntime]
    lens1 = [max(map(len, col)) for col in zip(*s1)]
    fmt1 = '\t'.join('{{:{}}}'.format(x) for x in lens1)
    table1 = [fmt1.format(*row) for row in s1]
    print('\n'.join(table1))

    with open(f"{benchmark.__DIRECTORY__}/statistics/AMSizeVsOptimisationFlagRuntime{lastExperiment['N']}.csv", "w", newline="") as f:
            f.write('\n'.join(table1))

    # 5.1.1 Print runtimes normalised to slowest 
    # Taken straight from stackoverflow: https://stackoverflow.com/questions/13214809/pretty-print-2d-list    
    
    slowest = outputRuntime[4][1]
    s1 = [[e if type(e) == str else str(round(e/slowest,2)) for e in row] for row in outputRuntime]
    lens1 = [max(map(len, col)) for col in zip(*s1)]
    fmt1 = '\t'.join('{{:{}}}'.format(x) for x in lens1)
    table1 = [fmt1.format(*row) for row in s1]
    print('\n'.join(table1))

    # 5.2. Write runtimes to file
    with open(f"{benchmark.__DIRECTORY__}/statistics/AMSizeVsOptimisationFlagRuntimeNormalisedP{lastExperiment['N']}.csv", "w", newline="") as f:
            f.write('\n'.join(table1))

    slowest = outputRuntime[4][1]
    s1 = [[e if type(e) == str else str(round(slowest/e,2)) for e in row] for row in outputRuntime]
    lens1 = [max(map(len, col)) for col in zip(*s1)]
    fmt1 = '\t'.join('{{:{}}}'.format(x) for x in lens1)
    table1 = [fmt1.format(*row) for row in s1]
    print('\n'.join(table1))

    # 5.2. Write runtimes to file
    with open(f"{benchmark.__DIRECTORY__}/statistics/AMSizeVsOptimisationFlagRuntimeSpeedup{lastExperiment['N']}.csv", "w", newline="") as f:
            f.write('\n'.join(table1))

    # 5.3. Print binary sizes
    print("")
    s = [[str(e) for e in row] for row in outputBinarySize]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in s]
    print('\n'.join(table))

    # 5.4 Write binary sizes to file
    with open(f"{benchmark.__DIRECTORY__}/statistics/AMSizeVsOptimisationFlagBinarySize{lastExperiment['N']}.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(outputBinarySize)
    print("------------------------------------------------------------------------------------")

# Main function that runs all tests for the different benchmarks included in the benchmarks array below
if __name__ == "__main__":
    print("Testing impact AM performance has on a system with different levels of optimisation.")
    benchmarks = [threadRing_4p2(), big_4p8_v1(), big_4p8_v2() ,producerConsumer_5p2(), trapezoid_6p12()]
    #benchmarks = [big_4p8_v2()]
    print("------------------------------------------------------------------------------------")
    for benchmark in benchmarks:
        runAmVsOptimisationTests(benchmark)
