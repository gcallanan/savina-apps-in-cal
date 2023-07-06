"""
Script that takes a selected savina benchmark and fixed experiment parameter 
values and builds an FPGA image fusing different reducer algorithms.

The resource utilisation of the different images is then written to file.
"""


import time
import utilities
import os
import re
import buildFpgaImages

# Import all the benchmarks
from benchmark import Benchmark
from big_4p8_v1 import big_4p8_v1
from big_4p8_v2 import big_4p8_v2
from trapezoid_6p12 import trapezoid_6p12
from producerConsumer_5p2 import producerConsumer_5p2
from threadRing_4p2 import threadRing_4p2

reductionAlgorithms = ["first", "knowledge-priorities", "informative-tests", "ordered-condition-checking"]

benchmark = producerConsumer_5p2()
experimentParams = utilities.generateExperimentParams(benchmark.getBuildParameters())
experimentParam = experimentParams[3]


startTime_s = time.time()
directory = benchmark.__DIRECTORY__
directoryTime = time.strftime('%Y%m%d_%H%M')

resourceUsageLogFile = f"{benchmark.__DIRECTORY__}/fpgabuilds/{directoryTime}_{benchmark.__BENCHMARK_NAME__}_reductionAlgorithms_resource_usage.txt"
buildFpgaImages.writeResourceUsageFileHeader(benchmark, resourceUsageLogFile)

for reductionAlgorithm in reductionAlgorithms:
    runningTime_s = round(time.time() - startTime_s, 2)
    print(
            f"{runningTime_s:07.2f} Running reductionAlgorithm \"{reductionAlgorithm}\" for {benchmark.__TOP_ACTOR_NAME__} with params:",
            experimentParam,
        )

    # 3.0 Write the experiment parameters to the CAL config file
    utilities.writeConfigFile(benchmark, experimentParam)

    # 3.1 Create the correct directory
    paramString = ''.join([f"_{k}{v}" for k,v in experimentParam.items()])
    directory = benchmark.__DIRECTORY__ + f"/fpgabuilds/{directoryTime}_{benchmark.__BENCHMARK_NAME__}_{reductionAlgorithm}" + paramString
    print(directory)
    
    # 3.2 Build the project
    buildFpgaImages.buildFpgaImage(benchmark, directory, reductionAlgorithm)

    # 3.3 Write all results to file
    buildFpgaImages.writeResourceUsage(benchmark, directory, resourceUsageLogFile, f"{reductionAlgorithm}_{paramString}")

    # Dont think this is necessary, was here for debugging and now I cant be bothered to remove it.
    time.sleep(30)

buildFpgaImages.writeResourceUsageFileFooter(resourceUsageLogFile)
    
utilities.writeConfigFile(benchmark, experimentParams[0])   
runningTime_s = round(time.time() - startTime_s, 2)
print(f"Done in {runningTime_s:07.2f}")

    

        