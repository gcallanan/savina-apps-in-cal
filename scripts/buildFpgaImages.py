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
from big_4p8 import big_4p8
from trapezoid_6p12 import trapezoid_6p12
from producerConsumer_5p2 import producerConsumer_5p2
from threadRing_4p2 import threadRing_4p2

# 1. Get experiment parameters
benchmarks = [threadRing_4p2(), big_4p8(), producerConsumer_5p2(), trapezoid_6p12()]
benchmark = benchmarks[2]
experimentParams = utilities.generateExperimentParams(benchmark.getBuildParameters())

# 2. Set up all variables required for running experiments
testIndex = 0
startTime_s = time.time()
numTests = len(experimentParams)
directory = benchmark.__DIRECTORY__
directoryTime = time.strftime('%Y%m%d_%H%M')
#directoryTime = "20230427_1156"

# 2.1 Create a common log file where everything is written to
resourceUsageLogFile = f"{benchmark.__DIRECTORY__}/fpgabuilds/{directoryTime}_{benchmark.__BENCHMARK_NAME__}_resource_usage.txt"
file = open(resourceUsageLogFile, "a") #x
file.write(f"File reporting FPGA resource usage for {benchmark.__BENCHMARK_NAME__} benchmark.\n")
file.write(f"+------------------------------+----------+---------------+--------------+---------------+-------+-------+\n")
file.write(f"|                              |                        Resource Use Percentage                          |\n")
file.write(f"| Experiment Name + Parameters | CLB LUTs | LUTs as Logic |  LUTs as Mem | CLG Registers | BRAM  |  DPS  |\n")
file.write(f"+------------------------------+----------+---------------+--------------+---------------+-------+-------+\n")
file.close()


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
    directory = benchmark.__DIRECTORY__ + f"/fpgabuilds/{directoryTime}_{benchmark.__BENCHMARK_NAME__}" + paramString
    command = f"mkdir -p {directory}"
    exitCode = os.system(command)
    if exitCode != 0:
        raise Exception(f"'{command}' returned non-zero exit code.")

    # 3.2 Run streamblocks to generate source files for vivado
    command = f"streamblocks vivado-hls --set experimental-network-elaboration=on --source-path {benchmark.__DIRECTORY__}:../streamblocks-examples/system --target-path {directory} {benchmark.__TOP_ACTOR_NAME__}"
    print(command)
    exitCode = os.system(command)
    if exitCode != 0:
        raise Exception(f"'{command}' returned non-zero exit code.")

    # 3.3 Run cmake to prepare vivado project
    command = f"cd {directory}/build && cmake .. -DHLS_CLOCK_PERIOD=3.3 -DFPGA_NAME=xcu200-fsgd2104-2-e -DPLATFORM=xilinx_u200_xdma_201830_2 -DUSE_VITIS=on -DCMAKE_BUILD_TYPE=Debug"
    print(command)
    exitCode = os.system(command)
    if exitCode != 0:
        raise Exception(f"'{command}' returned non-zero exit code.")

    # 3.4 Build the vivado project
    command = f"cd {directory}/build && cmake --build . --target {benchmark.__XCLBIN_NAME__} -v"
    print(command)
    exitCode = os.system(command)
    if exitCode != 0:
        raise Exception(f"'{command}' returned non-zero exit code.")

    # 4. Write all results to file
    vivadoLogFilePath = directory + "/build/_x/link/vivado/vpl/prj/prj.runs/impl_1/full_util_placed.rpt"
    print(vivadoLogFilePath)

    try:
        with open(vivadoLogFilePath) as file:
            lines = file.readlines()
    except Exception:
        lines = 0

    title = f"{benchmark.__BENCHMARK_NAME__}{paramString}"
    try:
        for line in lines:
            if(line.find("CLB LUTs") >= 0 and line.count("|") == 6):
                columnStart = line[:-2].rindex("|")
                CLB_LUT_percentage = line[columnStart+1:-2]
                # print(line)
                # print(CLB_LUT_percentage)
            elif (line.find("  LUT as Logic") >= 0 and line.count("|") == 6):
                columnStart = line[:-2].rindex("|")
                LUT_as_Logic_percentage = line[columnStart+1:-2]
                # print(line)
                # print(LUT_as_Logic_percentage)
            elif (line.find("  LUT as Memory") >= 0 and line.count("|") == 6):
                columnStart = line[:-2].rindex("|")
                LUT_as_Mem_percentage = line[columnStart+1:-2]
                # print(line)
                # print(LUT_as_Mem_percentage)
            elif (line.find("CLB Registers              |") >= 0 and line.count("|") == 6):
                columnStart = line[:-2].rindex("|")
                CLBReg_percentage = line[columnStart+1:-2]
                # print(line)
                # print(CLBReg_percentage)
            elif (line.find("Block RAM Tile") >= 0 and line.count("|") == 6):
                columnStart = line[:-2].rindex("|")
                BRAM_percentage = line[columnStart+1:-2]
                # print(line)
                # print(BRAM_percentage)
            elif (line.find("DSPs") >= 0 and line.count("|") == 6):
                columnStart = line[:-2].rindex("|")
                DSP_percentage = line[columnStart+1:-2]
                # print(line)
                # print(DSP_percentage)
        outputLine = f"|{title:<30}|   {CLB_LUT_percentage}|        {LUT_as_Logic_percentage}|       {LUT_as_Mem_percentage}|        {CLBReg_percentage}|{BRAM_percentage}|{DSP_percentage}|\n"
    except Exception:
        outputLine = f"|{title:<30}| Parsing results failed ... \n"

    with open(resourceUsageLogFile, "a") as file:
        file.write(outputLine)

    testIndex += 1

# 4. Reset config file to prevent git commit issues
utilities.writeConfigFile(
        benchmark, experimentParams[0]
    )   

with open(resourceUsageLogFile, "a") as file:
    file.write(f"+------------------------------+----------+---------------+--------------+---------------+-------+-------+\n")

runningTime_s = round(time.time() - startTime_s, 2)
print(f"Done in {runningTime_s:07.2f}")

# 5. Grab Reports and write to file
# file:///home/gareth/streamblocks/savina-apps-in-cal/5p2_producerConsumer/fpgabuilds/20230426_0940_producerConsumer_C1_P1/build/_x/link/vivado/vpl/prj/prj.runs/impl_1/full_util_placed.rpt