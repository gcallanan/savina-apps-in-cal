# Benchmark 4.8 in the Savina paper: Big

## General Outline

Big is a benchmark consisting of N messenger actors. Each messenger actor has a connection to every other messenger actor. A messenger sends a ping out on a random port and waits for a pong response from the same port. Each messenger performs P pings. A messenger waits for a pong response before sending the next ping.

The benchmark is configured by adjusting N and P.

A Savina implementation of this benchmark can be found in the [BigHabaneroActorBenchmark.scala](https://github.com/shamsimam/savina/blob/master/src/main/scala/edu/rice/habanero/benchmarks/big/BigHabaneroActorBenchmark.scala) with configuration parameters for this benchmark available in [BigConfig.java](https://github.com/shamsimam/savina/blob/master/src/main/java/edu/rice/habanero/benchmarks/big/BigConfig.java)

[BigNetwork.cal](./BigNetwork.cal) describes the overall network for the benchmark.

## Quick Run
From within the 4P8-big directory:
1. mkdir build
2. time tychoc  --set pretty-print-post-template-sub=off --set pretty-print-test=off  --set experimental-network-elaboration=on --source-path . --target-path build big.BigNetwork && cc build/*.c -o add && time ./add testOut