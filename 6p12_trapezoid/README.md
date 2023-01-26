time tychoc  --set pretty-print-post-template-sub=off --set pretty-print-test=off  --set experimental-network-elaboration=on --set phase-timer=off --set print-am-statistics-pre-reduction=off  --source-path . --target-path build trapezoid.Worker && cc build/*.c -o add && time ./add in out


A Savina implementation of this benchmark can be found in the [TrapezoidalHabaneroActorBenchmark.scala](https://github.com/shamsimam/savina/blob/master/src/main/scala/edu/rice/habanero/benchmarks/trapezoid/TrapezoidalHabaneroActorBenchmark.scala)

Lots of config info found in [TrapezoidalConfig.java](https://github.com/shamsimam/savina/blob/master/src/main/java/edu/rice/habanero/benchmarks/trapezoid/TrapezoidalConfig.java)

A coordinator sends a single message to each actor and receives a single reply from those actors. Each actor performs exactly one action