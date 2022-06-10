import os
from collections import defaultdict
from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd

import utility
from lines import Lines


@dataclass()
class SizeMetric():
    size_metric_name: str
    relevant_size_columns: [str]
    is_in_phase: int


class SizeLines(Lines):
    def __init__(self, options):
        super().__init__(options)
        if options.petri_net_type == 'CPN':
            self.size_metrics = [
                SizeMetric(
                    size_metric_name='color reduced size',
                    relevant_size_columns=['colored reduce place count', 'colored reduce transition count'],
                    is_in_phase=1
                ),
                SizeMetric(
                    size_metric_name='unfolded size',
                    relevant_size_columns=['unfolded place count', 'unfolded transition count'],
                    is_in_phase=2
                ),
                SizeMetric(
                    size_metric_name='reduced size',
                    relevant_size_columns=['reduced place count', 'reduced transition count'],
                    is_in_phase=3
                ),
            ]
        elif options.petri_net_type == 'PT':
            self.size_metrics = [
                SizeMetric(
                    size_metric_name='reduced size',
                    relevant_size_columns=['reduced place count', 'reduced transition count'],
                    is_in_phase=3
                ),
            ]

        self.computed_sizes = defaultdict(dict)
        self.name = 'size lines'

    def prepare_data(self):
        for metric in self.size_metrics:
            os.makedirs(self.graph_dir + f'\\{metric.size_metric_name}\\')

        for metric in self.size_metrics:
            metric_name = metric.size_metric_name
            for keep_percentage in self.keep_percentages:
                combined_df = pd.DataFrame()
                for index, data in enumerate(self.data_list):
                    # Drop rows with errors
                    data = data.drop(data[data['error'] <= metric.is_in_phase].index)

                    if len(data) == 0:
                        print(
                            f"Test full of error {metric.is_in_phase} or lower, so graphs cannot be made for metric ({metric.size_metric_name}) in class ({self.name}). Check the errors in: {self.options.test_names[index]}")
                        continue
                    res_df = pd.DataFrame()

                    columns_list = metric.relevant_size_columns
                    res_df[metric_name] = data[columns_list].sum(axis=1)
                    res_df.dropna(subset=[metric_name], inplace=True)
                    metric_data = ((res_df[f'{metric_name}'].sort_values(ascending=True)).reset_index()).drop(columns=
                                                                                                              'index')

                    n = int(metric_data.shape[0] * keep_percentage)
                    metric_data = metric_data.tail(n)

                    # Rename the column to include the name of the test
                    metric_data.rename(columns={f'{metric_name}': self.options.test_names[index]}, inplace=True)

                    # Either initialize or add to the combined dataframe for all csvs
                    if index == 0:
                        combined_df = metric_data
                        continue
                    combined_df = pd.concat([combined_df, metric_data], axis=1)

                self.computed_sizes[metric_name][keep_percentage] = combined_df

    def plot(self):
        for metric in self.size_metrics:
            metric_name = metric.size_metric_name
            for keep_percentage in self.keep_percentages:

                data_to_plot = self.computed_sizes[metric_name][keep_percentage]

                plot = self.create_lineplot_highlight_orig(data_to_plot)
                plot.set(
                    ylabel=f'Combined number of transition and places',
                    xlabel='queries')
                try:
                    plot.set(yscale="log")
                except:
                    plot.set(yscale="linear")
                #plt.legend(labels=utility.get_col_names(data_to_plot.columns), loc='upper left', borderaxespad=0)
                plt.legend(loc='upper left')
                plt.savefig(
                    self.graph_dir + f'{metric_name}\\largest_{keep_percentage * 100}%.svg',
                    bbox_inches='tight', dpi=600, format="svg")
                if keep_percentage == 0.25 and metric.size_metric_name == 'color reduced size':
                    plt.savefig(
                        self.graph_dir + f'..\\shown_in_thesis\\color_reduce_size_largest_{keep_percentage*100}.svg',
                        bbox_inches='tight', dpi=600, format="svg")
                plt.close()
