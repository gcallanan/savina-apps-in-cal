"""
@author: Gareth Callanan

Script that runs the BIG benchmark for multiple tests.

Takes about 1200 seconds to run on a 12 core (6 real, 12 virtual) laptop when
numTests=3, N_values=2..9 and P_values=1000..10000000.
"""


import os
import time
import struct
import csv

# 1. Set up
N_values = [2, 3, 4, 5, 6, 7, 8, 9]
P_values = [1000, 10000, 100000, 1000000, 10000000]
numTests = 3
totalTests = numTests * len(P_values) * len(N_values)

timesCompilation_s = [
    [[0] * numTests for i in range(len(P_values))] for j in range(len(N_values))
]
timesRuntime_s = [
    [[0] * numTests for i in range(len(P_values))] for j in range(len(N_values))
]

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
            retCode = os.system("rm -rf target && mkdir target")
            if retCode != 0:
                raise Exception(f"Return code equal to {retCode}, expected 0")

            # 2.3. Build and compile
            start = time.time()
            retCode = os.system(
                "tychoc --set experimental-network-elaboration=on --source-path . --target-path target big.BigNetwork && cc target/*.c -o calBinary"
            )
            if retCode != 0:
                raise Exception(f"Return code equal to {retCode}, expected 0")
            compileTime_s = time.time() - start

            # 2.4. Run
            start = time.time()
            retCode = os.system("./calBinary testOut")
            if retCode != 0:
                raise Exception(f"Return code equal to {retCode}, expected 0")
            runTime_s = time.time() - start

            timesCompilation_s[N_index][P_index][testIndex] = compileTime_s
            timesRuntime_s[N_index][P_index][testIndex] = runTime_s

            # 2.5 Check the value of testOut
            with open("testOut", mode="rb") as file:
                fileContent = file.read()
                checksum = struct.unpack("i", fileContent)
                if checksum[0] != N:
                    raise Exception(f"Checksum value: {checksum[0]}, expected {N}")

            testsDone += 1
            print(
                f"Test {testsDone} of {totalTests} ({round((testsDone)/totalTests*100,2)}%) done. N={N}, P={P}, repeat={testIndex}. Compile time {round(compileTime_s,2)}s. Runtime: {round(runTime_s,2)}s."
            )


# 3. Reset config file to prevent having to recommit to git
configFileContents = """namespace big:
    uint numMessengers = 5;
    uint numPingPongs = 1000000;
end
"""

f = open("config.cal", "w")
f.write(configFileContents)
f.close()

# 4. Work out all the averages
avgCompileTime_s = [[0] * len(P_values) for i in range(len(N_values))]
avgRuntime_s = [[0] * len(P_values) for i in range(len(N_values))]

for N_index in range(len(N_values)):
    for P_index in range(len(P_values)):
        # Can be done with numpy, but I am keeping the external libraries to a minimal
        avgCompileTime_s[N_index][P_index] = (
            sum(timesCompilation_s[N_index][P_index]) / numTests
        )
        avgRuntime_s[N_index][P_index] = (
            sum(timesRuntime_s[N_index][P_index]) / numTests
        )

# 5. Write to CSV

# 5.1 Append row and column labels
rowLabels = N_values

# 5.1.1 New row label column
for row, label in zip(avgRuntime_s, rowLabels):
    row.insert(0, label)

for row, label in zip(avgCompileTime_s, rowLabels):
    row.insert(0, label)

# 5.1.2 New column label row
avgRuntime_s = [["N\\P"] + P_values] + avgRuntime_s
avgCompileTime_s = [["N\\P"] + P_values] + avgCompileTime_s

# 5.2 Write to file
with open("runtimes.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(avgRuntime_s)

with open("compileTimesCoarse.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(avgCompileTime_s)

# 6. Done
print(f"Total Time: {round(time.time()-totalStartTime_s,2)} s")
