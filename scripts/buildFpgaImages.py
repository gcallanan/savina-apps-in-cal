"""
@author Gareth Callanan

A script that generates the vivado_hls backend for Streamblocks projects in order to examine how the
AM controller logic use scales as the actor scales.

This script is less polished and reusable than other scripts - it just runs, there is limited sanity 
checking. Sorry. 

We expect that the following is installed:
1. streamblocks-platforms repo
2. streamblocks-examples repo - I expect this repo to be in the same directory as the 
                                savina-apps-in-cal repo. It is directly navigated to from
                                this script
3. Vivado 2020.2
4. The Xilinx Alveo U200 Package for Vivado 2018.2 (Debian file is called: 
   xilinx-u200-xdma-201830.2-2580015_18.04.deb)
"""

import time
import utilities
import os
import re

# Import all the benchmarks
from benchmark import Benchmark
from big_4p8_v1 import big_4p8_v1
from big_4p8_v2 import big_4p8_v2
from trapezoid_6p12 import trapezoid_6p12
from producerConsumer_5p2 import producerConsumer_5p2
from threadRing_4p2 import threadRing_4p2

def buildFpgaImage(benchmark: Benchmark, buildDirectory: str, reducerAlgorithm: str):
    command = f"mkdir -p {buildDirectory}"
    command = f"mkdir -p {buildDirectory}/build"
    exitCode = os.system(command)
    if exitCode != 0:
        raise Exception(f"'{command}' returned non-zero exit code.")

    # 3.2 Run streamblocks to generate source files for vivado and processor
    # 3.2.1 For the processor platform component
    command = f"streamblocks multicore --set experimental-network-elaboration=on --set reduction-algorithm={reducerAlgorithm} --source-path {benchmark.__DIRECTORY__}:../streamblocks-examples/system --target-path {buildDirectory} --set partitioning=on {benchmark.__TOP_ACTOR_NAME__}{benchmark.__TOP_ACTOR_NAME_STREAMBLOCKS_SUFFIX__}"
    print(command)
    exitCode = os.system(command)
    if exitCode != 0:
        raise Exception(f"'{command}' returned non-zero exit code.")
    
    # 3.2.2 For the vivado platform component default-controller= qj or bc
    command = f"streamblocks vivado-hls --set experimental-network-elaboration=on --set default-controller=qj --set reduction-algorithm={reducerAlgorithm} --source-path {benchmark.__DIRECTORY__}:../streamblocks-examples/system --target-path {buildDirectory} --set partitioning=on {benchmark.__TOP_ACTOR_NAME__}{benchmark.__TOP_ACTOR_NAME_STREAMBLOCKS_SUFFIX__}"
    print(command)
    exitCode = os.system(command)
    if exitCode != 0:
        raise Exception(f"'{command}' returned non-zero exit code.")

    # 3.3 Run cmake to prepare the project
    command = f"cd {buildDirectory}/build && cmake .. -DHLS_CLOCK_PERIOD=3.3 -DFPGA_NAME=xcu200-fsgd2104-2-e -DPLATFORM=xilinx_u200_xdma_201830_2 -DUSE_VITIS=on -DCMAKE_BUILD_TYPE=Debug"
    print(command)
    exitCode = os.system(command)
    if exitCode != 0:
        raise Exception(f"'{command}' returned non-zero exit code.")

    # 3.4 Build the processor component of the project
    command = f"cd {buildDirectory}/build && cmake --build . --target {benchmark.__TOP_ACTOR_NAME_NO_PREPATH__}{benchmark.__TOP_ACTOR_NAME_STREAMBLOCKS_SUFFIX__} -v"
    print(command)
    exitCode = os.system(command)
    if exitCode != 0:
        raise Exception(f"'{command}' returned non-zero exit code.")

    # 3.5 Build the vivado part of the project
    command = f"cd {buildDirectory}/build && cmake --build . --target {benchmark.__XCLBIN_NAME__} -v"
    print(command)
    exitCode = os.system(command)
    if exitCode != 0:
        raise Exception(f"'{command}' returned non-zero exit code.")

def writeResourceUsageFileHeader(benchmark: Benchmark, resourceUsageLogFile :str):
    file = open(resourceUsageLogFile, "w")
    file.write(f"File reporting FPGA resource usage for '{benchmark.__BENCHMARK_NAME__}'.\n")
    file.write(f"+--------------------------------------------------+-----------------+-----------------+-----------------+-----------------+-------------+---------------+\n")
    file.write(f"|                                                  |                        Resource Use Percentage                                                      |\n")
    file.write(f"| Experiment Name + Parameters                     |    CLB LUTs     |  LUTs as Logic  |   LUTs as Mem   |  CLG Registers  |    BRAM     |      DPSs     |\n")
    file.write(f"+--------------------------------------------------+-----------------+-----------------+-----------------+-----------------+-------------+---------------+\n")
    file.write(f"|baseline resource consumption                     | 15.54 ( 183751 )| 13.77 ( 162797 )|  3.54 (  20954 )| 10.95 ( 258830 )| 17.25 (372 )|  0.15 (   10 )|\n")
    file.close()

def writeResourceUsage(benchmark: Benchmark, projectDirectory: str, resourceUsageLogFile: str, appendToFile: str):
    vivadoLogFilePath = projectDirectory + "/build/vivado-hls/_x/link/vivado/vpl/prj/prj.runs/impl_1/full_util_placed.rpt"
    print(vivadoLogFilePath)

    try:
        with open(vivadoLogFilePath) as file:
            lines = file.readlines()
    except Exception:
        lines = 0

    title = f"{benchmark.__BENCHMARK_NAME__}_{appendToFile}"
    try:
        for line in lines:
            if(line.find("CLB LUTs") >= 0 and line.count("|") == 6):
                strSplit = line.split("|")
                CLB_LUT_percentage = strSplit[5]
                CLB_LUT_value = strSplit[2]
                # print(line)
                # print(CLB_LUT_percentage)
            elif (line.find("  LUT as Logic") >= 0 and line.count("|") == 6):
                strSplit = line.split("|")
                LUT_as_Logic_percentage = strSplit[5]
                LUT_as_Logic_value = strSplit[2]
                # print(line)
                # print(LUT_as_Logic_percentage)
            elif (line.find("  LUT as Memory") >= 0 and line.count("|") == 6):
                strSplit = line.split("|")
                LUT_as_Mem_percentage = strSplit[5]
                LUT_as_Mem_value = strSplit[2]
                # print(line)
                # print(LUT_as_Mem_percentage)
            elif (line.find("CLB Registers              |") >= 0 and line.count("|") == 6):
                strSplit = line.split("|")
                CLBReg_percentage = strSplit[5]
                CLBReg_value = strSplit[2]
                # print(line)
                # print(CLBReg_percentage)
            elif (line.find("Block RAM Tile") >= 0 and line.count("|") == 6):
                strSplit = line.split("|")
                BRAM_percentage = strSplit[5]
                BRAM_value = round(float(strSplit[2]))
                # print(line)
                # print(BRAM_percentage)
            elif (line.find("DSPs") >= 0 and line.count("|") == 6):
                strSplit = line.split("|")
                DSP_percentage = strSplit[5]
                DSP_value = strSplit[2]
                # print(line)
                # print(DSP_percentage)
        outputLine = f"|{title:<50}|{CLB_LUT_percentage}({CLB_LUT_value:<7})|{LUT_as_Logic_percentage}({LUT_as_Logic_value:<7})|{LUT_as_Mem_percentage}({LUT_as_Mem_value:<7})|{CLBReg_percentage}({CLBReg_value:<7})|{BRAM_percentage}({BRAM_value:<4})|{DSP_percentage}({DSP_value:<4})|\n"
    except Exception:
        outputLine = f"|{title:<50}| Parsing results failed ... \n"

    with open(resourceUsageLogFile, "a") as file:
        file.write(outputLine)

def writeResourceUsageFileFooter(resourceUsageLogFile :str):
    with open(resourceUsageLogFile, "a") as file:
        file.write(f"+--------------------------------------------------+-----------------+-----------------+-----------------+-----------------+-------------+---------------+\n")

if __name__ == "__main__":

    # 1. Get experiment parameters
    benchmarks = [threadRing_4p2(), big_4p8_v1(), producerConsumer_5p2(), trapezoid_6p12(), big_4p8_v2()]
    benchmark = benchmarks[1]
    experimentParams = utilities.generateExperimentParams(benchmark.getAMScalingExperimentParameters())
    reducerAlgorithm = "ordered-condition-checking"



    # 2. Set up all variables required for running experiments
    testIndex = 0
    startTime_s = time.time()
    numTests = len(experimentParams)
    directory = benchmark.__DIRECTORY__
    directoryTime = time.strftime('%Y%m%d_%H%M')
    #directoryTime = "20230427_1156"

    # 2.1 Create a common log file where everything is written to
    resourceUsageLogFile = f"{benchmark.__DIRECTORY__}/fpgabuilds/{directoryTime}_{benchmark.__BENCHMARK_NAME__}_{reducerAlgorithm}_resource_usage.txt"
    writeResourceUsageFileHeader(benchmark, resourceUsageLogFile)
    count = 0

    # 3. Run all the experiments
    for experimentParam in experimentParams:
        runningTime_s = round(time.time() - startTime_s, 2)
        print(
                f"{runningTime_s:07.2f} Running runtime test {testIndex+1} of {numTests} for {benchmark.__TOP_ACTOR_NAME__} with params:",
                experimentParam,
            )

        # 3.0 Write the experiment parameters to the CAL config file
        utilities.writeConfigFile(benchmark, experimentParam)

        # 3.1 Create the correct directory
        paramString = ''.join([f"_{k}{v}" for k,v in experimentParam.items()])
        directory = benchmark.__DIRECTORY__ + f"/fpgabuilds/{directoryTime}_{benchmark.__BENCHMARK_NAME__}_{reducerAlgorithm}" + paramString
        print(directory)
        
        # 3.2 Build the project
        buildFpgaImage(benchmark, directory, reducerAlgorithm)

        # 3.3 Write all results to file
        writeResourceUsage(benchmark, directory, resourceUsageLogFile, paramString)
        

    # 4. Reset config file to prevent git commit issues
    utilities.writeConfigFile(
            benchmark, experimentParams[0]
        )   

    writeResourceUsageFileFooter(resourceUsageLogFile)

    runningTime_s = round(time.time() - startTime_s, 2)
    print(f"Done in {runningTime_s:07.2f}")

    # 5. Grab Reports and write to file
    # file:///home/gareth/streamblocks/savina-apps-in-cal/5p2_producerConsumer/fpgabuilds/20230426_0940_producerConsumer_C1_P1/build/_x/link/vivado/vpl/prj/prj.runs/impl_1/full_util_placed.rpt