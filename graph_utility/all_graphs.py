import datetime
import os
import shutil

import pandas as pd

import utility
from answers import AnswerSimplificationBars
from consistency import check_consistency
from graph_utility.rules import RuleUsage
from gui import Gui


def plot_all(options):
    # Get number of files in this directory, remove the ones we do not use
    # Can use this for the prints
    num_graphs = len(options.chosen_graphs)
    graphs_made = 0
    print("Creating graph objects")
    graph_objects = [
        AnswerSimplificationBars(options),
        RuleUsage(options),
        # lines(options)
    ]

    print(f"Making graphs: {num_graphs}")
    for graph in graph_objects:
        if graph.name in options.chosen_graphs:
            print(f"Making graph: {graph.name}")
            graph.prepare_data()
            graph.plot()
            graphs_made += 1
            print(f"graphs made: {graphs_made}/{num_graphs}")


if __name__ == "__main__":
    options = Gui().get_options()

    # Remove all graphs
    if os.path.isdir(options.graph_dir):
        shutil.rmtree(options.graph_dir)
    os.makedirs(options.graph_dir)

    print("Sanitising the data")
    # todo
    options.read_results = utility.sanitise_df_list(
        [pd.read_csv(options.result_dir + "\\" + csv) for csv in options.results_to_plot])

    if options.enable_graphs:
        print("---------Creating graphs---------")
        plot_all(options)
        with open(options.graph_dir + "/graphs-meta.txt", mode='a') as file:
            file.write('Made graphs at at %s.\n' %
                       (datetime.datetime.now()))

    if options.do_consistency_check:
        print("---------Doing consistency check---------")
        check_consistency(options)
        with open(options.graph_dir + "/consistency-meta.txt", mode='a') as file:
            file.write('Did consistency check at %s.\n' %
                       (datetime.datetime.now()))
