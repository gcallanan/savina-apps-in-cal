# Benchmark 5.2 in the Savina paper: Producer-Consumer with Bounded-Buffer.

## General Outline

The Producer-Consumer with a Bounded-Buffer is a benchmark consisting of P producer actors and C consumer actors connected by a single buffer actor of size B. The producers send tokens to the buffer actor which stores them in a buffer. When a consumer is not busy, it sends a request for work to the buffer. The buffer actor will record which consumers are free and transmits data tokens to them when it receives them.

The benchmark is configured by adjusting P, C and B.

The producer and consumer actors are relativly simple, the buffer actor is more complex having to scale by P, C and B.

A Savina implementation of this benchmark can be found in the [ProdConsHabaneroActorBenchmark.scala](https://github.com/shamsimam/savina/blob/master/src/main/scala/edu/rice/habanero/benchmarks/bndbuffer/ProdConsHabaneroActorBenchmark.scala) with configuration parameters for this benchmark available in [ProdConsBoundedBufferConfig.java](https://github.com/shamsimam/savina/blob/master/src/main/java/edu/rice/habanero/benchmarks/bndbuffer/ProdConsBoundedBufferConfig.java)

[BndBufferNetwork.cal](./BndBufferNetwork.cal) describes the overall network for the benchmark.

A producer only produces items if it receives a request to do so and it has not yet produced numItemsPerProducer items. It is not expected that a producer will receive another work request after it has already received one and before it has completed the request.

A consumer sends a request for items when it is not busy. Only a single request is sent. The buffer will track which consumer have requested items and assign when ready.

The buffer only transmits items to a consumer if there is a request for work from that consumer. The buffer actor will request new items from the producers when there is space on the internal buffer array. NOTE: If there are 3 spaces available on the buffer and 2 producers are busy producing items while 3 other producers are free, then the buffer will only request 1 of them to produce an item. This eliminates the risk of getting more items from producers than there is space available in the buffer

## Quick Run
From within the 5p2_producerConsumer directory:
1. mkdir build
2. time tychoc  --set pretty-print-post-template-sub=off --set pretty-print-test=off  --set experimental-network-elaboration=on --set phase-timer=off --set print-am-statistics-pre-reduction=off  --source-path . --target-path build bndBuffer.BndBufferNetwork && cc build/*.c -o add -lm && time ./add
