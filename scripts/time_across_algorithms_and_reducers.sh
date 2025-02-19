# !/bin/bash

echo "Network,Reducer,Prefire Cycles,Total Cycles,Total Runtime(ms),Params">temp.csv

run_experiment () {
    #dir=4p8_big_v1
    #network=BigNetworkStreamblocks
    #class=big
    #r=ordered-condition-checking

    dir=$1
    network=$2
    class=$3
    r=$4

    cd $dir

    echo "Building $dir/$class.$network with $r"
    config=$(tail -n +2 config.cal | head -n -1| tr -d '\n')

    streamblocks multicore --set reduction-algorithm=$r --set experimental-network-elaboration=on --source-path .:../streamblocks-examples/system --target-path myproject $class.$network 2>/dev/null
    cd myproject/build/
    cmake .. -D TRACE=ON 2>&1 /dev/null
    cmake --build . -j24 2> /dev/null
    cd ../bin

    echo "Testing $dir/$class.$network with $r"

    prefire_sum=0
    total_sum=0
    runtime_sum=0
    num_tests=30
    for i in $(seq $num_tests); 
    do 
        start=`date +%s%N`
        res=$(numactl -C 1 ./$network --timing)
        end=`date +%s%N`
        runtime=$( echo "$end - $start" | bc -l )
        runtime=$(($runtime/1000000))
        prefire_time=$(echo $res | grep -Po '(?<=(prefire: )).*(?= cycles)')
        total_time=$(echo $res | grep -Po '(?<=(total: )).*(?=nsleep)')
        echo "    Completed test $i: $prefire_time    $total_time    $runtime" 
        prefire_sum=$(($prefire_sum+$prefire_time))
        total_sum=$(($total_sum+$total_time))
        runtime_sum=$(($runtime_sum+$runtime))
    done
    prefire_sum=$(($prefire_sum/$num_tests))
    total_sum=$(($total_sum/$num_tests))
    runtime_sum=$(($runtime_sum/$num_tests))
    cd ../..
    rm -r myproject
    cd ..
    echo "$dir/$class.$network,$r,$prefire_sum,$total_sum,$runtime_sum,$config" >> temp.csv
}

if [ ! -d "streamblocks-examples" ]; then
   echo "Missing the streamblocks-examples repository in this directory. It is required to call the sqrt() function."
   echo "Pull with 'git clone https://github.com/streamblocks/streamblocks-examples.git'"
   exit 1
fi


run_experiment joiner JoinerNetworkStreamblocks joiner ordered-condition-checking
run_experiment joiner JoinerNetworkStreamblocks joiner informative-tests
run_experiment joiner JoinerNetworkStreamblocks joiner first

# run_experiment 5p2_producerConsumer BndBufferNetworkSb bndBuffer ordered-condition-checking
# run_experiment 5p2_producerConsumer BndBufferNetworkSb bndBuffer informative-tests
# run_experiment 5p2_producerConsumer BndBufferNetworkSb bndBuffer first

# run_experiment 4p8_big_v2 BigNetworkStreamblocks big ordered-condition-checking
# run_experiment 4p8_big_v2 BigNetworkStreamblocks big informative-tests
# run_experiment 4p8_big_v2 BigNetworkStreamblocks big first

# run_experiment 4p8_big_v1 BigNetworkStreamblocks big ordered-condition-checking
# run_experiment 4p8_big_v1 BigNetworkStreamblocks big informative-tests
# run_experiment 4p8_big_v1 BigNetworkStreamblocks big first

