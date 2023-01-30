# Benchmark 5.2 in the Savina paper: Producer-Consumer with Bounded-Buffer.

## General Outline

The Producer-Consumer with a Bounded-Buffer is a benchmark consisting of P producer actors and C consumer actors connected by a single buffer actor of size B. The producers send tokens to the buffer actor which stores them in a buffer. When a consumer is not busy, it sends a request for work to the buffer. The buffer actor will record which consumers are free and transmits data tokens to them when it receives them.

The benchmark is configured by adjusting P, C and B.

The producer and consumer actors are relativly simple, the buffer actor is more complex having to scale by P, C and B.

A Savina implementation of this benchmark can be found in the [ProdConsHabaneroActorBenchmark.scala](https://github.com/shamsimam/savina/blob/master/src/main/scala/edu/rice/habanero/benchmarks/bndbuffer/ProdConsHabaneroActorBenchmark.scala) with configuration parameters for this benchmark available in [ProdConsBoundedBufferConfig.java](https://github.com/shamsimam/savina/blob/master/src/main/java/edu/rice/habanero/benchmarks/bndbuffer/ProdConsBoundedBufferConfig.java)

## Quick Run
From within the 6p12-trapezoid directory:
1. mkdir build
2. time tychoc  --set pretty-print-post-template-sub=off --set pretty-print-test=off  --set experimental-network-elaboration=on --set phase-timer=off --set print-am-statistics-pre-reduction=on  --source-path . --target-path build trapezoid.TrapezoidNetwork && cc build/*.c -o add -lm && time ./add testOut
