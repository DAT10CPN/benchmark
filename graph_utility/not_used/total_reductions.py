import copy

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import graph_utility.utility as utility


def plot(data_list, test_names, graph_dir, category):
    """
        Plots 3 bars for each experiment, one for how many transitions, places and both has been reduced
    """

    # The deepcopies are because in the 'all_graphs' the data_list are used for all plots,
    # so each function will make their own copy
    data_list = copy.deepcopy(data_list)
    test_names = copy.deepcopy(test_names)

    # Remove test with no reductions
    data_list, test_names = utility.remove_no_red(data_list, test_names)

    # List to hold the reductions for each experiment
    total_reductions = []
    transitions_reductions = []
    places_reductions = []
    # Go through each experiment
    for test_index, data in enumerate(data_list):
        transition_reduction_sum = data['prev transition count'].sum() - data['post transition count'].sum()
        place_reduction_sum = data['prev place count'].sum() - data['post place count'].sum()

        total_reductions.append(place_reduction_sum + transition_reduction_sum)
        transitions_reductions.append(transition_reduction_sum)
        places_reductions.append(place_reduction_sum)

    # Create dataframe
    points_df = pd.DataFrame(
        {'total': total_reductions, 'places': places_reductions, 'transitions': transitions_reductions})

    # Rename indices to be test names, instead of int index
    points_df = utility.rename_index_to_test_name(points_df, test_names)
    # data_to_plot = utility.split_into_all_with_without(points_df)
    # png_names = ['all', 'with', 'without']
    points_df.rename(utility.rename_test_name_for_paper_presentation(test_names), axis='rows', inplace=True)
    if len(points_df) != 0 and len(points_df.columns) != 0:
        # Plot the plot
        sns.set_theme(style="darkgrid", palette="pastel")
        plot = points_df.plot(kind='barh', width=0.75, linewidth=2, figsize=(10, 10))

        plt.legend(bbox_to_anchor=(1.02, 1), loc='best', borderaxespad=0)
        plt.xscale('log')
        plt.xlabel("reductions")
        plt.ylabel('experiments-30-60-1-1')

        # Plot the numbers in the bars
        for p in plot.patches:
            left, bottom, width, height = p.get_bbox().bounds
            plot.annotate(int(width), xy=(left + width, bottom + height / 2),
                          ha='center', va='center')

        plt.savefig(graph_dir + f'{category}_total_reductions.svg', bbox_inches='tight', dpi=600, format="svg")
        plt.close()
