# Benchmark 6.12 in the Savina paper: Trapezoid Approximation

## General Outline

Trapezoidal approximation is a benchmark consisting of W worker actors and a single coordinator actor.
The objective is to approximate the integral of the function: `f(x) = 1/(1+x) * sqrt(1 + e^(sqrt(2x))) * sin(x^3 - 1)` using trapezoidal approximation where a total of N trapezoids are calculated.

The coordinator executes two actions. The first distributes the integral to the W workers. Each worker calculates and sums N/W trapezoids in exactly one action. The second action then collects the results from every actor and sums them all together outputing the total area. This is simlilar to creating multiple threads to perform a small section of work each and then collection their results together after a `.join()`

The benchmark is configured by adjusting W and N.

A Savina implementation of this benchmark can be found in the [TrapezoidalHabaneroActorBenchmark.scala](https://github.com/shamsimam/savina/blob/master/src/main/scala/edu/rice/habanero/benchmarks/trapezoid/TrapezoidalHabaneroActorBenchmark.scala) with configuration parameters for this benchmark available in [TrapezoidalConfig.java](https://github.com/shamsimam/savina/blob/master/src/main/java/edu/rice/habanero/benchmarks/trapezoid/TrapezoidalConfig.java)

[TrapezoidNetwork.cal](./TrapezoidNetwork.cal) describes the overall network for the benchmark.

## Quick Run
From within the 6p12-trapezoid directory:
1. mkdir build
2. time tychoc  --set pretty-print-post-template-sub=off --set pretty-print-test=off  --set experimental-network-elaboration=on --set phase-timer=off --set print-am-statistics-pre-reduction=on  --source-path . --target-path build trapezoid.TrapezoidNetwork && cc build/*.c -o add -lm && time ./add testOut
