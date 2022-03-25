import os
from collections import defaultdict
from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

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

        self.computed_sizes = defaultdict(dict)
        self.name = 'size lines'
        for metric in self.size_metrics:
            os.makedirs(self.graph_dir + f'\\{metric.size_metric_name}\\')

    def prepare_data(self):
        for metric in self.size_metrics:
            metric_name = metric.size_metric_name
            for keep_percentage in self.keep_percentages:
                combined_df = pd.DataFrame()
                for index, data in enumerate(self.data_list):
                    # Drop rows with errors
                    data.drop(data[data['error'] <= metric.is_in_phase].index, inplace=True)

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
        sns.set_theme(style="darkgrid")
        for metric in self.size_metrics:
            metric_name = metric.size_metric_name
            for keep_percentage in self.keep_percentages:

                data_to_plot = self.computed_sizes[metric_name][keep_percentage]

                custom_palette = {}
                for column_index, column in enumerate(data_to_plot.columns):
                    custom_palette[column] = utility.color((column_index + 1) / len(data_to_plot.columns))

                my_dashes = self.linestyles[0:len(data_to_plot.columns) - 1]

                columns_without_base = [column for column in data_to_plot.columns if column != self.base_name]
                if not (len(data_to_plot) == 0 or len(data_to_plot.columns) == 0):
                    if self.base_name in self.options.test_names:
                        sns.lineplot(data=data_to_plot[self.base_name], palette=custom_palette,
                                     linewidth=self.base_width)
                        plot = sns.lineplot(data=data_to_plot[columns_without_base], palette=custom_palette,
                                            linewidth=self.other_width,
                                            dashes=my_dashes)
                    else:
                        plot = sns.lineplot(data=data_to_plot, palette=custom_palette)
                    plot.set(
                        ylabel=f'Combined number of transition and places',
                        xlabel='queries')
                    plot.set(yscale="linear")
                    plt.legend(loc='upper left', borderaxespad=0)

                    plt.savefig(
                        self.graph_dir + f'{metric_name}\\largest_{keep_percentage * 100}%.svg',
                        bbox_inches='tight', dpi=600, format="svg")
                    plt.close()
