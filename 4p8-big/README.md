Messenger: tychoc  --set pretty-print-post-template-sub=on --set pretty-print-test=off  --set experimental-network-elaboration=on --source-path . --target-path target big.MessengerWrapper && cc target/*.c -o add && ./add in1 in2 in3 in4 out1 out2 out3 out4

Sink: tychoc  --set pretty-print-post-template-sub=on --set pretty-print-test=off  --set experimental-network-elaboration=on --source-path . --target-path target big.SinkWrapper && cc target/*.c -o add && ./add in1 in2 in3 in4 out1 out2 out3 out4

Network: time tychoc  --set pretty-print-post-template-sub=off --set pretty-print-test=off  --set experimental-network-elaboration=on --source-path . --target-path target big.BigNetwork && cc target/*.c -o add && time ./add testOut


// Issues

1. The template substitition creates maaaaany actors for certain input parameters to a network

// Quick run 

1. mkdir target
2. time tychoc  --set pretty-print-post-template-sub=off --set pretty-print-test=off  --set experimental-network-elaboration=on --source-path . --target-path target big.BigNetwork && cc target/*.c -o add && time ./add testOut

Output in testOut
Configuration parameters in config.cal