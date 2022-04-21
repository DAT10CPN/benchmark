import datetime
import os
import shutil

import pandas as pd

import utility
from answers import AnswerSimplificationBars
from consistency import check_consistency
from unique_results import find_unique_results
from graph_utility.lines_memory_state import MemoryStateLines
from graph_utility.lines_size import SizeLines
from graph_utility.lines_time import TimeLines
from graph_utility.rules import RuleUsage
from graph_utility.debug import DebugGraph
from gui import Gui


def plot_graphs(options):
    # Get number of files in this directory, remove the ones we do not use
    # Can use this for the prints
    num_graphs = len(options.chosen_graphs)
    graphs_made = 0

    print("Creating graph objects")
    graph_objects = [
        AnswerSimplificationBars(options),
        RuleUsage(options),
        MemoryStateLines(options),
        TimeLines(options),
        SizeLines(options),
        DebugGraph(options)
    ]

    print(f"Making graphs: {num_graphs}")
    for graph in graph_objects:
        if graph.name in options.chosen_graphs:
            print("-----------")
            print(f"Making graph: {graph.name}")
            try:
                graph.prepare_data()
                graph.plot()
            except Exception as e:
                print(f"\033[93mGraph failed with exception: {e}\033[0m")
            graphs_made += 1
            print(f"graphs made: {graphs_made}/{num_graphs}")


if __name__ == "__main__":
    options = Gui().get_options()

    # Remove all graphs
    if os.path.isdir(options.graph_dir):
        shutil.rmtree(options.graph_dir)
    os.makedirs(options.graph_dir)

    print("---------Sanitising the data---------")
    options.read_results = utility.sanitise_df_list(options)


    with open(options.graph_dir + "/meta.txt", mode='a') as file:
        file.write('Ran at %s.\n' %
                   (datetime.datetime.now()))

    if options.debug:
        print("---------Printing errors graphs---------")
        os.makedirs(options.graph_dir + "\\errors")
        utility.write_results_with_errors(options)

    if (options.enable_graphs > 0) or options.debug:
        print("---------Creating graphs---------")
        plot_graphs(options)

    if options.unique_results:
        print("---------Finding unique results---------")
        find_unique_results(options)

    if options.do_consistency_check:
        print("---------Doing consistency check---------")
        check_consistency(options)

    print("---------Finished---------")