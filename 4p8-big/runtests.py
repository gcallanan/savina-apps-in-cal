import os
import time
import struct

# 1. Set up
N_values = [2,3,4,5,6]
P_values = [1000,10000, 100000,1000000,10000000]
numTests = 1
totalTests = numTests * len(P_values) * len(N_values)

timesCompilation_s = [[ [0]*numTests for i in range(len(P_values))] for j in range(len(N_values))]
timesRuntime_s = [[ [0]*numTests for i in range(len(P_values))] for j in range(len(N_values))]

totalStartTime_s = time.time()

# 2. Loop through the experiements
testsDone = 0
for testIndex in range(numTests):
    for N_index in range(len(N_values)):
        for P_index in range(len(P_values)):
            
            N = N_values[N_index]
            P = P_values[P_index]
            # 2.1. Set config.cal
            configFileContents = f"""
            namespace big:
                uint numMessengers = {N};
                uint numPingPongs = {P};
            end
            """

            f = open("config.cal", "w")
            f.write(configFileContents)
            f.close()


            # 2.2. remove and recreate target directory
            os.system("rm -rf target && mkdir target")

            # 2.3. Build and compile
            start = time.time()
            os.system("tychoc --set experimental-network-elaboration=on --source-path . --target-path target big.BigNetwork && cc target/*.c -o calBinary")
            compileTime_s = time.time() - start

            # 2.4. Run
            start = time.time()
            os.system("./calBinary testOut")
            runTime_s = time.time() - start

            #print(f"For N = {N}, P = {P}:")
            #print(f"\t{compileTime_s} compile time")
            #print(f"\t{runTime_s} run time")

            timesCompilation_s[N_index][P_index][testIndex] = compileTime_s
            timesRuntime_s[N_index][P_index][testIndex] = runTime_s

            # 2.5 Check the value of testOut
            with open("testOut", mode='rb') as file: # b is important -> binary
                fileContent = file.read()
                checksum = struct.unpack("i",fileContent)
                if(checksum[0] != N):
                    raise Exception(f"Checksum value: {checksum[0]}, expected {N}") 

            testsDone += 1
            print(f"Test {testsDone} of {totalTests} ({round((testsDone)/totalTests*100,2)}) done. N={N}, P={P}, repeat={testIndex}. Compile time {round(compileTime_s,2)}s. Runtime: {round(runTime_s,2)}s.")


# 3. Reset config file to prevent having to recommit to git
configFileContents = f"""
namespace big:
    uint numMessengers = 5;
    uint numPingPongs = 1000000;
end
"""

f = open("config.cal", "w")
f.write(configFileContents)
f.close()

# 4. Work out all the averages 
avgCompileTime_s = [ [0]*len(P_values) for i in range(len(N_values))]
avgRuntime_s = [ [0]*len(P_values) for i in range(len(N_values))]

for N_index in range(len(N_values)):
    for P_index in range(len(P_values)):
        avgCompileTime_s[N_index][P_index] = sum(timesCompilation_s[N_index][P_index])/numTests # Can be done with numpy, but I am keeping the external libraries to a minimal
        avgRuntime_s[N_index][P_index] = sum(timesRuntime_s[N_index][P_index])/numTests

# 5. Write to CSV


# 6. Done
print(f"Total Time: {round(time.time()-totalStartTime_s,2)} s")