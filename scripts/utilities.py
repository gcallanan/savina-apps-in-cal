import os
import string
import time
import subprocess
import csv
import benchmark as benchmark

from typing import List
from dataclasses import dataclass


@dataclass
class RuntimeExperimentResults:
    experimentParameters: dict
    runTime_s: float


@dataclass
class CompileTimeExperimentResults:
    experimentParameters: dict
    compileTime_s: float
    phasesTimingOutput: str
    amSizeOutput: str
    preAmSizeMeasurement: bool


def makeDataDir(exper: benchmark.Benchmark):
    directory = exper.__DIRECTORY__
    command = f"mkdir -p {directory}/data"
    retCode = os.system(command)
    if retCode != 0:
        raise Exception(
            f"Could not create directory '{directory}/data'. Return code equal to {retCode}, expected 0"
        )


def buildActor(
    actorName: string,
    directory: string,
    phase_timers: bool = False,
    reduction_algorithm: string = "informative-tests", #<(first | random | shortest-path-to-exec | informative-tests | informative-tests-if-true | informative-tests-if-false)>
    am_statistics_post_reduction: bool = False,
    am_statistics_pre_reduction: bool = False, # Can take a very long time or crash when compiling
    compile_C_to_binary: bool = True, # Compile the generated C files to a binary
    timeout_s = 100000,
) -> None:
    
    phase_timers_flag = ""
    if phase_timers:
        phase_timers_flag = "--set phase-timer=on"

    am_statistics_post_reduction_flag = ""
    if am_statistics_post_reduction:
        am_statistics_post_reduction_flag = "--set print-am-statistics-post-reduction=on"

    am_statistics_pre_reduction_flag = ""
    if am_statistics_pre_reduction:
        am_statistics_pre_reduction_flag = "--set print-am-statistics-pre-reduction=on"

    # 1. remove and recreate target directory
    command = f"rm -rf {directory}/build && mkdir {directory}/build"
    retCode = os.system(command)
    if retCode != 0:
        raise Exception(
            f"Could not build {actorName}. Return code equal to {retCode}, expected 0"
        )

    # 2 Build and compile, capture the output
    # --set reduction-algorithm=random
    # <(first | random | shortest-path-to-exec | informative-tests | informative-tests-if-true | informative-tests-if-false)>
    command = f"tychoc --set experimental-network-elaboration=on  --set reduction-algorithm={reduction_algorithm} --set reporting-level=error {am_statistics_post_reduction_flag} {am_statistics_pre_reduction_flag} {phase_timers_flag} --source-path {directory} --target-path {directory}/build {actorName}"
    start = time.time()
    procRet = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, timeout=timeout_s)
    err = procRet.stderr
    out = procRet.stdout
    if (err != ''): 
        raise RuntimeError(
            f"Return code equal to {err}, expected 0 when compiling {actorName}"
        )
    compileTime_s = time.time() - start

    # 3. Generate binary from C
    if compile_C_to_binary:
        command = f"cc  {directory}/build/*.c -o {directory}/build/calBinary -lm"
        exitCode = os.system(command)
        if exitCode != 0:
            raise Exception(
                f"'{command}' returned non-zero exit code when compiling C for {actorName}."
            )

    return out, compileTime_s


def runActor(
    directory: string, inputFileList: List[str], outputFileList: List[str]
) -> None:

    inputArgumentFileNames = " ".join(inputFileList)
    outputArgumentsFileName = " ".join(outputFileList)
    command = f"{directory}/build/calBinary {inputArgumentFileNames} {outputArgumentsFileName}"

    start = time.time()
    exitCode = os.system(command)
    if exitCode != 0:
        raise Exception(f"'{command}' returned non-zero exit code.")
    runTime_s = time.time() - start

    return runTime_s


def writeConfigFile(exper: benchmark.Benchmark, experimentParam: List[dict]):
    fileDirectory = exper.__DIRECTORY__
    contents = exper.getConfigFileContents(**experimentParam)
    f = open(fileDirectory + "/config.cal", "w")
    f.write(contents)
    f.close()

def writeCompilerPhaseFiles(directory: string, results: List[CompileTimeExperimentResults], reduction_algorithm, fileNameAppend: str,) -> List[List]:
    command = f"mkdir -p {directory}/statistics"
    retCode = os.system(command)
    if retCode != 0:
        raise Exception(
            f"Could not create directory '{directory}/statistics'. Return code equal to {retCode}, expected 0"
        )
    
    
    expParamsHeading = ["key: " + x for x in results[0].experimentParameters.keys()]

    phaseTitles = expParamsHeading + ["Total Runtime (ms)"]
    csvOutput = []

    first = True
    for output in results:
        totalRuntimeTime_ms = 0
        expParamsValues = [
            output.experimentParameters[x] for x in output.experimentParameters.keys()
        ]
        timingResults = expParamsValues + [0]

        for line in iter(output.phasesTimingOutput.splitlines()):
            # Skip the first line as it contains information that we do not need.
            if line == "Execution time report:":
                continue
                
            # line formated as: '<phasename> (<time> ms)' need to unpack this
            openParenthIndex = line.rindex("(")
            endDigitIndex = line.rindex(" ms)")

            # If this is the first test, we also need to extract phase titles
            if first:
                phaseTitle = line[: openParenthIndex - 1]
                phaseTitles.append(phaseTitle)

            runtime_ms = int(line[openParenthIndex + 1 : endDigitIndex])
            totalRuntimeTime_ms += runtime_ms
            timingResults.append(runtime_ms)

        if first:
            first = False
            csvOutput.append(phaseTitles)

        timingResults[len(expParamsHeading)] = totalRuntimeTime_ms # This is the row one after the headings row
        csvOutput.append(timingResults)

    # Switch rows and columns as this is easier to read
    csvOutput = list(map(list, zip(*csvOutput)))

    append=reduction_algorithm.replace("-","").upper()
    with open(f"{directory}/statistics/compilePhaseTimes_{fileNameAppend}_{append}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csvOutput)


def writeAmStatisticsResults(
    directory: string,
    results: List[CompileTimeExperimentResults],
    fileNameAppend: str,
    reduction_algorithm: str
) -> List[List]:

    command = f"mkdir -p {directory}/statistics"
    retCode = os.system(command)
    if retCode != 0:
        raise Exception(
            f"Could not create directory '{directory}/statistics'. Return code equal to {retCode}, expected 0"
        )


    titles = ["key: preOrPostReduction"] + ["key: " + x for x in results[0].experimentParameters.keys()]
    csvOutput = []

    first = True
    for output in results:

        lines = output.amSizeOutput.split("\n")

        if first:
            first = False
            titles = titles + lines[0].split(",")
            csvOutput.append(titles)

        for line in lines[1:]:
            if line == "":
                continue

            preTag = "pre" if output.preAmSizeMeasurement else "post"

            expParamsValues = [preTag] + [
                output.experimentParameters[x]
                for x in output.experimentParameters.keys()
            ]
            csvOutput.append(expParamsValues + line.split(","))
    
    append=reduction_algorithm.replace("-","").upper()
    with open(f"{directory}/statistics/amSizeStatistics_{fileNameAppend}_{append}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csvOutput)


def writeRuntimeFiles(
    directory: string, results: List[RuntimeExperimentResults], depVarKey: string, reduction_algorithm: string
):
    command = f"mkdir -p {directory}/statistics"
    retCode = os.system(command)
    if retCode != 0:
        raise Exception(
            f"Could not create directory '{directory}/statistics'. Return code equal to {retCode}, expected 0"
        )

    # Generate our array for results
    formatedResults = {}
    for output in results:
        newDict = dict(output.experimentParameters)
        del newDict[depVarKey]

        key = "_".join([str(output.experimentParameters[x]) for x in newDict.keys()])

        if not key in formatedResults:
            formatedResults[key] = {}

        formatedResults[key][output.experimentParameters[depVarKey]] = output.runTime_s

    # create a nicely formated list
    independentVars = [x for x in newDict.keys()]
    depVarsValues = [x for x in formatedResults[key].keys()]
    depVarsTitles = [depVarKey + "=" + str(x) for x in formatedResults[key].keys()]

    csvOutput = [independentVars + depVarsTitles]

    for key, depVarDict in formatedResults.items():
        keyVals = key.split("_") if key != "" else []
        depResults = [formatedResults[key][x] for x in depVarsValues]
        csvOutput.append(keyVals + depResults)

    append=reduction_algorithm.replace("-","").upper()
    with open(f"{directory}/statistics/runtimes_{append}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csvOutput)
