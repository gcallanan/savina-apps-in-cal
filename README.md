# Savina Apps in CAL

Run Savaina benchmarks using Tycho and the CAL actor language.

To run all the experiemnts execute `python3 scripts/runExperiments.py` from the terminal. Note this can take hours to run, so be ready. 

All apps here taken from the Savina Actor Benchmark paper.

@inproceedings{10.1145/2687357.2687368,
    author = {Imam, Shams M. and Sarkar, Vivek},
    title = {Savina - An Actor Benchmark Suite: Enabling Empirical Evaluation of Actor Libraries},
    year = {2014},
    isbn = {9781450321891},
    publisher = {Association for Computing Machinery},
    address = {New York, NY, USA},
    url = {https://doi.org/10.1145/2687357.2687368},
    doi = {10.1145/2687357.2687368},
    abstract = {This paper introduces the Savina benchmark suite for actor-oriented programs. Our goal is to provide a standard benchmark suite that enables researchers and application developers to compare different actor implementations and identify those that deliver the best performance for a given use-case. The benchmarks in Savina are diverse, realistic, and represent compute (rather than I/O) intensive applications. They range from popular micro-benchmarks to classical concurrency problems to applications that demonstrate various styles of parallelism. Implementations of the benchmarks on various actor libraries are made publicly available through an open source release. This will allow other developers and researchers to compare the performance of their actor libraries on these common set of benchmarks.},
    booktitle = {Proceedings of the 4th International Workshop on Programming Based on Actors Agents & Decentralized Control},
    pages = {67–80},
    numpages = {14},
   keywords = {performance comparison, benchmark suite, java actor libraries, actor model},
   location = {Portland, Oregon, USA},
   series = {AGERE! '14}
}

The github for the Savina framework is available [here](https://github.com/shamsimam/savina).

# Requirements
1. [streamblocks-tycho](https://git.cs.lth.se/dataflow/streamblocks-tycho) on the LU gitlab servers has been installed and you are using branch "EntityRenamingBug" branch. We use the the tychoc binary in the streamblocks-tycho repo, not the streamblocks binary in the [streamblocks-platforms](https://git.cs.lth.se/dataflow/streamblocks-tycho/-/tree/EntityRenamingBug) repo to build.