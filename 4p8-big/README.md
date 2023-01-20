# General Outline

Big is a benchmark consisting of N messenger actors. Each messenger actor has a connection to every other messenger actor. A messenger sends a ping out on a random port and waits for a pong response from the same port. Each messenger performs P pings. A messenger waits for a pong response before sending the next ping.

The benchmark is configured by adjusting N and P.

A Savina implementation of this benchmark can be found in the [BigHabaneroActorBenchmark.scala](https://github.com/shamsimam/savina/blob/master/src/main/scala/edu/rice/habanero/benchmarks/big/BigHabaneroActorBenchmark.scala)

# Requirements
1. [streamblocks-tycho](https://git.cs.lth.se/dataflow/streamblocks-tycho) on the LU gitlab servers has been installed and you are using branch "EntityRenamingBug" branch. We use the the tychoc binary in the streamblocks-tycho repo, not the streamblocks binary in the [streamblocks-platforms](https://git.cs.lth.se/dataflow/streamblocks-tycho/-/tree/EntityRenamingBug) repo to build.

# Quick Run
From within the 4P8-BIG directory
1. mkdir target
2. time tychoc  --set pretty-print-post-template-sub=off --set pretty-print-test=off  --set experimental-network-elaboration=on --source-path . --target-path target big.BigNetwork && cc target/*.c -o add && time ./add testOut

Alternativly:
- Running `python3 runtests.py` will run a script that runs over a range of N and P values and generates CSV files describing total compilation and running times.
- Running `python3 compileTimeMeasurements.py` will run a script that runs over a range of N values and generating a CSV file describing the compilation times for different phases giving more granular insight into the compilation process.


# Potential Issues
1. The template substitition results in a new set of source code being generated for each actor. This may not always be necessary and can result in lots of code being generated.