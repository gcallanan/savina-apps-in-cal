"""
@author Gareth Callanan

TODO

Have to put in installation requirements

Expect streamblocks-examples/system
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


benchmarks = [threadRing_4p2(), big_4p8(), producerConsumer_5p2(), trapezoid_6p12()]

benchmark = benchmarks[2]

experimentParams = utilities.generateExperimentParams(benchmarks[2].getBuildParameters())
testIndex = 0
startTime_s = time.time()
numTests = len(experimentParams)
directory = benchmark.__DIRECTORY__

for experimentParam in experimentParams:
    directory = benchmark.__DIRECTORY__ + f"/fpgabuilds/{time.strftime('%Y%m%d_%H%M')}_{benchmark.__BENCHMARK_NAME__}" + ''.join([f"_{k}{v}" for k,v in experimentParam.items()])

    runningTime_s = round(time.time() - startTime_s, 2)
    print(
            f"{runningTime_s:07.2f} Running runtime test {testIndex+1} of {numTests} for {benchmark.__TOP_ACTOR_NAME__} with params:",
            experimentParam,
        )
    utilities.writeConfigFile(benchmark, experimentParam)

    # 1. Create the correct directory
    command = f"mkdir -p {directory}"
    exitCode = os.system(command)
    if exitCode != 0:
        raise Exception(f"'{command}' returned non-zero exit code.")

    # 2. Run streamblocks to generate source files for vivado
    command = f"streamblocks vivado-hls --set experimental-network-elaboration=on --source-path {benchmark.__DIRECTORY__}:../streamblocks-examples/system --target-path {directory} {benchmark.__TOP_ACTOR_NAME__}"
    print(command)
    exitCode = os.system(command)
    if exitCode != 0:
        raise Exception(f"'{command}' returned non-zero exit code.")

    # 3. Switch to build directory to run cmake
    command = f"cd {directory}/build && cmake .. -DHLS_CLOCK_PERIOD=3.3 -DFPGA_NAME=xcu200-fsgd2104-2-e -DPLATFORM=xilinx_u200_xdma_201830_2 -DUSE_VITIS=on -DCMAKE_BUILD_TYPE=Debug"
    print(command)
    exitCode = os.system(command)
    if exitCode != 0:
        raise Exception(f"'{command}' returned non-zero exit code.")

    command = f"cd {directory}/build && cmake --build . --target {benchmark.__XCLBIN_NAME__} -v"
    print(command)
    exitCode = os.system(command)
    if exitCode != 0:
        raise Exception(f"'{command}' returned non-zero exit code.")

    testIndex += 1
    break

utilities.writeConfigFile(
        benchmark, experimentParams[0]
    )   # reset to prevent git commit issues