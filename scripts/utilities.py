import os
import string
import time
import subprocess
import csv
import scripts.benchmark as benchmark

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

def makeDataDir(exper: benchmark.Benchmark):
    directory = exper.__DIRECTORY__
    command = f"mkdir -p {directory}/data"
    retCode = os.system(command)
    if retCode != 0:
        raise Exception(f"Could not create directory '{directory}/data'. Return code equal to {retCode}, expected 0")


def buildActor(actorName: string, directory: string, phase_timers: bool = False, am_statistics: bool = False) -> None:
    phase_timers_flag = ""
    if(phase_timers):
        phase_timers_flag = "--set phase-timer=on"

    am_statistics_flag = ""
    if(am_statistics):
        am_statistics_flag = "--set print-am-statistics=on"
    
    # 1. remove and recreate target directory
    command = f"rm -rf {directory}/build && mkdir {directory}/build"
    retCode = os.system(command)
    if retCode != 0:
        raise Exception(f"Could not build {actorName}. Return code equal to {retCode}, expected 0")

    # 2 Build and compile, capture the output
    command = f"tychoc --set experimental-network-elaboration=on {am_statistics_flag} {phase_timers_flag} --source-path {directory} --target-path {directory}/build {actorName}"
    start = time.time()
    proc = subprocess.Popen(
        [
            command,
            ".",
        ],
        stdout=subprocess.PIPE,
        shell=True,
    )
    (out, err) = proc.communicate()
    if (
        err is not None
    ):  # This error check does not work yet - always returns none even if the command fails
        raise Exception(f"Return code equal to {err}, expected 0 when compiling {actorName}")
    compileTime_s = time.time() - start

    # 3. Generate binary from C
    command = f"cc  {directory}/build/*.c -o {directory}/build/calBinary"
    exitCode = os.system(command)
    if exitCode != 0:
        raise Exception(f"'{command}' returned non-zero exit code when compiling C for {actorName}.")


    return out.decode("ASCII"), compileTime_s

def runActor(directory: string, inputFileList: List[str], outputFileList: List[str]) -> None:
    
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

def writeCompilerFiles(directory: string, results: List[CompileTimeExperimentResults]):
    command = f"mkdir -p {directory}/statistics"
    retCode = os.system(command)
    if retCode != 0:
        raise Exception(f"Could not create directory '{directory}/statistics'. Return code equal to {retCode}, expected 0")
    
    csvData = formatPhaseTimingResults(results)
    with open(f"{directory}/statistics/compilePhaseTimes.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csvData)

    csvData = formatAmStatisticsResults(results)
    with open(f"{directory}/statistics/amSizeStatistics.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csvData)

def formatPhaseTimingResults(results: List[CompileTimeExperimentResults]) -> List[List]:
    expParamsHeading = ["key: " + x for x in results[0].experimentParameters.keys()]

    phaseTitles = expParamsHeading + ["Total Runtime (ms)"]
    csvOutput = []

    first = True
    for output in results:
        totalRuntimeTime_ms = 0
        expParamsValues = [output.experimentParameters[x] for x in output.experimentParameters.keys()]
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

        timingResults[1] = totalRuntimeTime_ms
        csvOutput.append(timingResults)

    # Switch rows and columns as this is easier to read
    csvOutput = list(map(list, zip(*csvOutput)))

    return csvOutput

def formatAmStatisticsResults(results: List[CompileTimeExperimentResults]) -> List[List]:
    titles = ["key: " + x for x in results[0].experimentParameters.keys()]
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
            expParamsValues = [output.experimentParameters[x] for x in output.experimentParameters.keys()]
            csvOutput.append(expParamsValues + line.split(","))

    return csvOutput

def writeRuntimeFiles(directory: string, results: List[RuntimeExperimentResults], depVarKey: string):
    command = f"mkdir -p {directory}/statistics"
    retCode = os.system(command)
    if retCode != 0:
        raise Exception(f"Could not create directory '{directory}/statistics'. Return code equal to {retCode}, expected 0")
    
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
        keyVals = key.split("_")
        depResults = [formatedResults[key][x] for x in depVarsValues]
        csvOutput.append(keyVals + depResults)

    with open(f"{directory}/statistics/runtimes.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csvOutput)

    

