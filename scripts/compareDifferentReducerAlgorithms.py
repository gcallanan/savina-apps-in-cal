import utilities
import time
import subprocess
import csv

from typing import List
from typing import Dict

from benchmark import Benchmark
from trapezoid_6p12 import trapezoid_6p12
from producerConsumer_5p2 import producerConsumer_5p2
from threadRing_4p2 import threadRing_4p2
from big_4p8_temp import big_4p8_temp
from big_4p8 import big_4p8


resultsMapPerExperiment = {}
def processResults(compilerAmOutput) -> None:
    if(compilerAmOutput == "-"):
        for actorName in resultsMapPerExperiment:
            resultsMapPerExperiment[actorName].append([-1,-1])
    else:
        first = True
        for line in iter(compilerAmOutput.splitlines()):
            if(first):
                first = False
                continue
            actorName = line.split(',')[0]
            numStates = line.split(',')[1]
            numConditions = line.split(',')[2]

            if(actorName in resultsMapPerExperiment):
                resultsMapPerExperiment[actorName].append([numStates,numConditions])
            else:
                resultsMapPerExperiment[actorName] = [[numStates,numConditions]]

def resetResultsPerExperiment() -> None:
    global resultsMapPerExperiment
    resultsMapPerExperiment = {}
    
def writeResultsToFile(benchmark: Benchmark, reducerAlgorithms: List[str], experimentParams: Dict[str,int],resultsMap: Dict[str,Dict[str,str]]) -> None:
    actors = list(resultsMap[reducerAlgorithms[0]].keys())
    scalingAttributes = '_'.join(list(experimentParams[0].keys()))
    
    # Get results
    output = []
    for actor in actors:
        output.append([actor])
        output.append([scalingAttributes, "conditions"] + reducerAlgorithms)
        for i in range(len(experimentParams)):
            paramValues = "_".join(str(x) for x in list(experimentParams[i].values()))
            #stateCount = resultsMap[reducerAlgorithm][actor][i]
            #print(resultsMap[reducerAlgorithms[0]][actor])
            
            # Sometimes the value of the condition is -1, sweep thourhg until its not
            numConditions = "-1"
            for j in range(len(reducerAlgorithms)):
                if(numConditions == "-1"):
                    numConditions = str(resultsMap[reducerAlgorithms[j]][actor][i][1])

            stateCount = [resultsMap[x][actor][i][0] for x in reducerAlgorithms]
            output.append([paramValues, numConditions] + stateCount)

    with open(f"{benchmark.__DIRECTORY__}/statistics/reducerAlgorithmComparison.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(output)

    



if __name__ == "__main__":
    benchmarks = [threadRing_4p2(), big_4p8(), producerConsumer_5p2(), trapezoid_6p12(), big_4p8_temp()]
    #benchmarks = [big_4p8() ]#big_4p8(),producerConsumer_5p2()]
    reducerAlgorithms = utilities.getReductionAlgorithms()
    #reducerAlgorithms = ["informative-tests", "knowledge-priorities"]

    startTime_s = time.time()
    for benchmark in benchmarks:
        resultsMapPerReducer = {}

        for reducerAlgorithm in reducerAlgorithms:
            
            runningTime_s = round(time.time() - startTime_s, 2)
            print(
                f'{runningTime_s:07.2f} Benchmark: "{benchmark.__BENCHMARK_NAME__}" with algorithm: "{reducerAlgorithm}"'
            )

            experimentParams = utilities.generateExperimentParams(
                benchmark.getAMScalingParameters()
            )
            numTests = len(experimentParams)
            testIndex = 0
            
            failedOne = False
            for experimentParam in experimentParams:
                
                if(not failedOne):
                    runningTime_s = round(time.time() - startTime_s, 2)
                    print(
                        f"\t{runningTime_s:07.2f} Running compile test {testIndex+1} of {numTests} for {benchmark.__TOP_ACTOR_NAME__} with params:",
                        experimentParam,
                    )

                    testIndex += 1

                    utilities.writeConfigFile(benchmark, experimentParam)
                    try:
                        compilerAmOutput, compileTime_s, binarySize_bytes = utilities.buildActor(
                            benchmark.__TOP_ACTOR_NAME__,
                            benchmark.__DIRECTORY__,
                            am_statistics_post_reduction=True,
                            reduction_algorithm=reducerAlgorithm,
                            compile_C_to_binary=False,
                            timeout_s=600,
                        )
                    except subprocess.TimeoutExpired:
                        print("\t\tTimed out on compilation. Skipping the rest of the tests for this reducer algorithm")
                        failedOne = True
                        compilerAmOutput = "-"
                    except RuntimeError:
                        print("\t\tCompilation failed. Suspect heap space issue. Skipping the rest of the tests for this reducer algorithm")
                        failedOne = True
                        compilerAmOutput = "-"

                else:
                    compilerAmOutput = "-"

                processResults(compilerAmOutput)

            utilities.writeConfigFile(
                benchmark,
                experimentParams[0],
            )  # reset to prevent git commit issues

            print("")

            resultsMapPerReducer[reducerAlgorithm] = resultsMapPerExperiment
            resetResultsPerExperiment()
        writeResultsToFile(benchmark, reducerAlgorithms, experimentParams,resultsMapPerReducer)
        print("\n\n")

    runningTime_s = round(time.time() - startTime_s, 2)
    print(f"{runningTime_s:07.2f} Done")



