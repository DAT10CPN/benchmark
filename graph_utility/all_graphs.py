import datetime
import os
import shutil

import utility
from answer_simplification_bars import answer_simplification_bars
from gui import Gui
from lines import lines
from ruleusage import RuleUsage
from check_consistency import check_consistency


def plot_all(options):
    # Get number of files in this directory, remove the ones we do not use
    # Can use this for the prints
    num_graphs = len(options['test names'])
    graphs_made = 0

    # Sanitise the data
    print("Sanitising the data")
    options['chosen results'] = utility.sanitise_df_list(options['chosen results'])

    print("Creating graph objects")
    graph_objects = [
        answer_simplification_bars(options),
        RuleUsage(options),
        lines(options)
    ]

    print(f"Making graphs: {num_graphs}")
    print(f"{graphs_made}/{num_graphs} graphs made")
    for graph in graph_objects:
        if graph.name in options['chosen graphs']:
            print(f"Making graph: {graph.name}")
            graph.read_results()
            graph.prepare_data()
            graph.plot()
            print(f"graphs made: {graphs_made}/{num_graphs}")
            graphs_made += 1


if __name__ == "__main__":
    options = Gui().get_options()

    # Remove all graphs
    if os.path.isdir(options.graph_dir):
        shutil.rmtree(options.graph_dir)
    os.makedirs(options.graph_dir)

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
