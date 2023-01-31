# Benchmark 4.2 in the Savina paper: Thread Ring.

## General Outline

Thread Ring is a benchmark consisting of N actors connected to to each other in a ring. A token is passed around this ring. The token starts with the value R and this value is decremented by 1 on each transmission. Transmission stops when the value being passed by the token

The benchmark is configured by adjusting N (the number of actors).

This benchmark is very simple, requiring very simple actors

A Savina implementation of this benchmark can be found in the [ThreadRingHabaneroActorBenchmark.scala](https://github.com/shamsimam/savina/blob/master/src/main/scala/edu/rice/habanero/benchmarks/threadring/ThreadRingHabaneroActorBenchmark.scala) with configuration parameters for this benchmark available in [ThreadRingConfig.java](https://github.com/shamsimam/savina/blob/master/src/main/java/edu/rice/habanero/benchmarks/threadring/ThreadRingConfig.java)

[ThreadRing.cal](./ThreadRing.cal) Describes both the actors making up the ring and the network joining these actors together.

## Quick Run
From within the 4p8_threadRing directory:
1. mkdir build
2. time tychoc  --set pretty-print-post-template-sub=off --set pretty-print-test=off  --set experimental-network-elaboration=on --set phase-timer=off --set print-am-statistics-pre-reduction=off  --source-path . --target-path build threadRing.ThreadRing && cc build/*.c -o add -lm && time ./add