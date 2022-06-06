import datetime
import os
import shutil
import seaborn as sns
import utility
from answers import AnswerSimplificationBars
from consistency import check_consistency
from graph_utility.debug import DebugGraph
from graph_utility.lines_memory_state import MemoryStateLines
from graph_utility.lines_size import SizeLines
from graph_utility.lines_time import TimeLines
from graph_utility.ratios import Ratios
from graph_utility.rules import RuleUsage
from graph_utility.ratios_per_model import ModelRatios
from graph_utility.ratios_per_model_averages_first import ModelRatiosAverages
from graph_utility.time_saved import TimeSaved
from graph_utility.answers_per_model import AnswersByModel
from gui import Gui
from unique_results import find_unique_results


def plot_graphs(options):
    # Get number of files in this directory, remove the ones we do not use
    # Can use this for the prints
    num_graphs = len(options.chosen_graphs)
    graphs_made = 0

    if not options.all_options:
        print("Creating graph objects")

    sns.set_theme(style="darkgrid")
    graph_objects = [
        #AnswerSimplificationBars(options),
        #RuleUsage(options),
        #MemoryStateLines(options),
        #TimeLines(options),
        #SizeLines(options),
        #DebugGraph(options),
        #Ratios(options),
        #ModelRatios(options),
        #ModelRatiosAverages(options),
        TimeSaved(options)
        #AnswersByModel(options)
    ]

    if not options.all_options:
        print(f"Making graphs: {num_graphs}")
    for graph in graph_objects:
        if graph.name in options.chosen_graphs:
            if not options.all_options:
                print("-----------")
                print(f"Making graph: {graph.name}")
            #try:
            graph.prepare_data()
            graph.plot()
            #except Exception as e:
             #   print(f"\033[93mGraph failed with exception: {e}\033[0m")
            graphs_made += 1
            if not options.all_options:
                print(f"graphs made: {graphs_made}/{num_graphs}")


if __name__ == "__main__":
    options_list = Gui().get_options()

    if len(options_list) > 1:
        print(f"Creating graphs for multiple directories: {len(options_list)}")
        print(
            f"\033[91mNeed to be run \033[0m- \033[93mProbalby not needed \033[0m- \033[92mWe have the results\033[0m")

    for index, options in enumerate(options_list):
        test_name = "{:<25}".format(options.folder_name) + "{:<25}".format(options.category) + "{:<10}".format(
            options.search_strategy) + "{:<20}".format(options.model_folder)
        progress = f"{index + 1}/{len(options_list)}"
        progress = "{:<7}".format(progress)
        if len(options.results_to_plot) == 0:
            if "inhib" in options.model_folder or options.folder_name != 'CPN-4-30-4-2-ioless':
                print(f"{progress} - \033[93mSKIPPING, NO RESULTS     \033[0m: {test_name}")
            else:
                print(f"{progress} - \033[91mSKIPPING, NO RESULTS     \033[0m: {test_name}")
                graph_dir = os.path.join(os.path.dirname(__file__), f"..\\graphs\\")
                with open(graph_dir + "\\tests_to_run.txt", mode='a') as file:
                    file.write(test_name + "\n")
            continue

        if os.path.isdir(options.graph_dir) and not options.overwrite:
            print(f"{progress} - \033[92mSKIPPING, WONT OVERWRITE \033[0m: {test_name}")
            continue

        if options.all_options:
            print(f"{progress} - \033[92mGENERATING GRAPHS        \033[0m: {test_name}")

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
        utility.sanity_check_is_rule_used(options)

        if (options.enable_graphs > 0) or options.debug:
            if not options.all_options:
                print("---------Creating graphs---------")
            os.makedirs(options.graph_dir + "\\for_exam")
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
