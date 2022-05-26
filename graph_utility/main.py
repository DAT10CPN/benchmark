import datetime
import os
import shutil

import utility
from answers import AnswerSimplificationBars
from consistency import check_consistency
from graph_utility.debug import DebugGraph
from graph_utility.lines_memory_state import MemoryStateLines
from graph_utility.lines_size import SizeLines
from graph_utility.lines_time import TimeLines
from graph_utility.ratios import VerificationTimeRatio
from graph_utility.rules import RuleUsage
from gui import Gui
from unique_results import find_unique_results


def plot_graphs(options):
    # Get number of files in this directory, remove the ones we do not use
    # Can use this for the prints
    num_graphs = len(options.chosen_graphs)
    graphs_made = 0

    if not options.all_options:
        print("Creating graph objects")
    graph_objects = [
        AnswerSimplificationBars(options),
        RuleUsage(options),
        MemoryStateLines(options),
        TimeLines(options),
        SizeLines(options),
        DebugGraph(options),
        VerificationTimeRatio(options)
    ]

    if not options.all_options:
        print(f"Making graphs: {num_graphs}")
    for graph in graph_objects:
        if graph.name in options.chosen_graphs:
            if not options.all_options:
                print("-----------")
                print(f"Making graph: {graph.name}")
            try:
                graph.prepare_data()
                graph.plot()
            except Exception as e:
                print(f"\033[93mGraph failed with exception: {e}\033[0m")
            graphs_made += 1
            if not options.all_options:
                print(f"graphs made: {graphs_made}/{num_graphs}")


if __name__ == "__main__":
    options_list = Gui().get_options()

    if len(options_list) > 1:
        print(f"Creating graphs for multiple directories: {len(options_list)}")

    for index, options in enumerate(options_list):
        if len(options.results_to_plot) == 0:
            continue

        test_name = options.result_dir.split('results')[1].replace('\\', '-')[1:]
        if os.path.isdir(options.graph_dir) and not options.overwrite:
            print(f"Skipping, in order to not overwrite: {index}/{len(options_list)} - {test_name}")
            continue

        if options.all_options:
            print(f"Working on: {index}/{len(options_list)} - {test_name}")

        # Remove all graphs
        if os.path.isdir(options.graph_dir):
            shutil.rmtree(options.graph_dir)
        os.makedirs(options.graph_dir)

        if not options.all_options:
            print("---------Sanitising the data---------")
        options.read_results = utility.sanitise_df_list(options)

        with open(options.graph_dir + "/meta.txt", mode='a') as file:
            file.write('Ran at %s.\n' %
                       (datetime.datetime.now()))

        if options.debug:
            if not options.all_options:
                print("---------Printing errors graphs---------")
            os.makedirs(options.graph_dir + "\\errors")
            utility.write_results_with_errors(options)

        if (options.enable_graphs > 0) or options.debug:
            if not options.all_options:
                print("---------Creating graphs---------")
            plot_graphs(options)

        if options.unique_results:
            if not options.all_options:
                print("---------Finding unique results---------")
            find_unique_results(options)

        if options.do_consistency_check:
            if not options.all_options:
                print("---------Doing consistency check---------")
            check_consistency(options)

        if not options.all_options:
            print("---------Finished---------")

    if len(options_list) > 1:
        print(f"Finished with: {len(options_list)}/{len(options_list)}")
