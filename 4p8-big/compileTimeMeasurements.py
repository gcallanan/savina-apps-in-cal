"""
@author: Gareth Callanan

Script that compiles the big benchmark for different values of N and reports the time taken for each
compilation phase in Tycho to run. Allows for fine grained examination of the Tycho compiler.

Takes about 1200 seconds to run on a 12 core (6 real, 12 virtual) laptop when numTests=3,
N_values=2..9 and P_values=1000..10000000.
"""

import os
import time
import subprocess
import csv

# 1. Setup
N_values = [2, 3, 4, 5, 6, 7, 8, 9]
totalTests = len(N_values)
testsDone = 0

outputs = []

# 2. Run compilation with the '--set phase-timer=on' to record the timing of each flag
for N_index in range(len(N_values)):
    N = N_values[N_index]
    # 2.1. Set config.cal
    configFileContents = f"""
    namespace big:
        uint numMessengers = {N};
        uint numPingPongs = 1000000;
    end
    """

    f = open("config.cal", "w")
    f.write(configFileContents)
    f.close()

    # 2.2. remove and recreate target directory
    retCode = os.system("rm -rf target && mkdir target")
    if retCode != 0:
        raise Exception(f"Return code equal to {retCode}, expected 0")

    # 2.3. Build and compile, capture the output
    start = time.time()
    proc = subprocess.Popen(
        [
            "tychoc --set experimental-network-elaboration=on --set phase-timer=on --source-path . --target-path target big.BigNetwork",
            ".",
        ],
        stdout=subprocess.PIPE,
        shell=True,
    )
    (out, err) = proc.communicate()
    if err is None:  # This error check does not work yet - always returns none even if the command fails
        raise Exception(f"Return code equal to {err}, expected 0")
    compileTime_s = time.time() - start
    outputs.append(out)

    testsDone += 1
    print(
        f"Test {testsDone} of {totalTests} ({round((testsDone)/totalTests*100,2)}%) done. N={N}. Compile time {round(compileTime_s,2)}s.."
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

# 4. Extract the timing information from the outputs and store in a 2D list
phaseTitles = ["Title\\N"]
csvOutput = []

first = True
for N, output in zip(N_values, outputs):

    timingResults = [N]

    for line in iter(output.splitlines()):
        # Skip the first line as it contains information that we do not need.
        line = line.decode("ASCII")
        if line == "Execution time report:":
            continue

        # line formated as: '<phasename> (<time> ms)' need to unpack this
        openParenthIndex = line.rindex("(")
        endDigitIndex = line.rindex(" ms)")

        # If this is the first test, we also need to extract phase titles
        if first:
            phaseTitle = line[: openParenthIndex - 1]
            phaseTitles.append(phaseTitle)

        runtime_ms = int(line[openParenthIndex + 1: endDigitIndex])
        timingResults.append(runtime_ms)

    if first:
        first = False
        csvOutput.append(phaseTitles)

    csvOutput.append(timingResults)

# Switch rows and columns as this is easier to read
csvOutput = list(map(list, zip(*csvOutput)))

# 5. Write results to a CSV file.
with open("compileTimesFine.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(csvOutput)
