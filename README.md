# Savina Apps in CAL

Run Savina benchmarks using Tycho and the CAL actor language.

To run all the experiments execute `python3 scripts/runSavinaBenchmark.py` from the terminal. Note this can take hours to run, so be ready.

All apps here taken from the Savina Actor Benchmark paper:

@inproceedings{10.1145/2687357.2687368,
    author = {Imam, Shams M. and Sarkar, Vivek},
    title = {Savina - An Actor Benchmark Suite: Enabling Empirical Evaluation of Actor Libraries},
    year = {2014},
    isbn = {9781450321891},
    publisher = {Association for Computing Machinery},
    address = {New York, NY, USA},
    url = {https://doi.org/10.1145/2687357.2687368},
    doi = {10.1145/2687357.2687368},
    booktitle = {Proceedings of the 4th International Workshop on Programming Based on Actors Agents & Decentralized Control},
    pages = {67–80},
    numpages = {14},
   keywords = {performance comparison, benchmark suite, java actor libraries, actor model},
   location = {Portland, Oregon, USA},
   series = {AGERE! '14}
}

The github for the Savina framework is available [here](https://github.com/shamsimam/savina).

In order to compare the impact of an actor machine size vs c optimisation flags, run `python3 scripts/amSizeVsOptimisationFlagComparison.py` from the terminal.

Each benchmark directory has its own README describing how it was constructed and how to run it individually

# Requirements
1. The streamblocks-tÿcho repo is required. A copy is available on [gitlab](https://git.cs.lth.se/dataflow/streamblocks-tycho/-/tree/da843c022de456b31dcf97cbff7685d3442a0517) the Lund University servers (this may or may not be public) or on the the open source Streamblocks github repo. The branch tested in the github repo with this benchmark suite can be found [here](https://github.com/streamblocks/streamblocks-tycho/tree/29c39f1bfb1264dcdad09349a733bd7aa260fed0). We use the the tychoc binary in the streamblocks-tycho repo, not the streamblocks binary in the [streamblocks-platforms](https://git.cs.lth.se/dataflow/streamblocks-tycho/-/tree/EntityRenamingBug) repo to build these benchmarks.

# Bugs
1. consumers = [Consumer(consCost=consCost): for i in 0..C-1]; Actors require a dummy variable to be inisialised in this list.