# Requirements
1. [streamblocks-tycho](https://git.cs.lth.se/dataflow/streamblocks-tycho) on the LU gitlab servers has been installed and you are using branch "EntityRenamingBug" branch. We use the the tychoc binary in the streamblocks-tycho repo, not the streamblocks binary in the [streamblocks-platforms](https://git.cs.lth.se/dataflow/streamblocks-tycho/-/tree/EntityRenamingBug) repo to build.

# Quick Run
From within the 4P8-BIG directory
1. mkdir target
2. time tychoc  --set pretty-print-post-template-sub=off --set pretty-print-test=off  --set experimental-network-elaboration=on --source-path . --target-path target big.BigNetwork && cc target/*.c -o add && time ./add testOut

# Potential Issues
1. The template substitition results in a new set of source code being generated for each actor. This may not always be necessary and can result in lots of code being generated.