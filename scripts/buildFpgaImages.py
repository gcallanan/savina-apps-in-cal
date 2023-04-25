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
    directory = benchmark.__DIRECTORY__ + f"/fpgabuilds/{directoryTime}_{benchmark.__BENCHMARK_NAME__}" + ''.join([f"_{k}{v}" for k,v in experimentParam.items()])
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

    testIndex += 1
    break

# 4. Reset config file to prevent git commit issues
utilities.writeConfigFile(
        benchmark, experimentParams[0]
    )   

runningTime_s = round(time.time() - startTime_s, 2)
print(f"Done in {runningTime_s:07.2f}")