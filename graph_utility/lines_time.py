import os
from collections import defaultdict

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import utility
from lines import Lines


class TimeLines(Lines):
    def __init__(self, options):
        super().__init__(options)
        self.name = 'time lines'
        self.times = defaultdict(dict)
        self.time_metrics = ['verification time', 'colored reduce time', 'unfold time', 'reduce time', 'total time']
        for metric in self.time_metrics:
            os.makedirs(self.graph_dir + f'\\{metric}\\')

    def prepare_data(self):
        for metric in self.time_metrics:
            for cutoff_time in self.cutoff_times:
                combined_df = pd.DataFrame()
                for index, data in enumerate(self.data_list):
                    data = utility.remove_errors_df(data)
                    res_df = pd.DataFrame()
                    if metric == 'total time':
                        res_df['total time'] = data[data['answer'] != 'NONE'].apply(
                            utility.get_total_time,
                            axis=1)
                    else:
                        res_df[metric] = data[metric]

                    res_df.dropna(subset=[metric], inplace=True)
                    metric_data = ((res_df[metric].sort_values()).reset_index()).drop(columns='index')
                    metric_data = metric_data[metric_data[metric] >= cutoff_time]
                    # Rename the column to include the name of the test
                    metric_data.rename(columns={metric: self.options.test_names[index]}, inplace=True)

                    # Either initialize or add to the combined dataframe for all csvs
                    if index == 0:
                        combined_df = metric_data
                        continue
                    combined_df = pd.concat([combined_df, metric_data], axis=1)
                # combined_df.rename(utility.rename_test_name_for_paper_presentation(self.options.test_names), axis='columns',
                # inplace=True)
                self.times[metric][cutoff_time] = combined_df

    def plot(self):
        sns.set_theme(style="darkgrid")
        for cutoff_time in self.cutoff_times:
            for metric in self.time_metrics:
                data_to_plot = self.times[metric][cutoff_time]

                if len(data_to_plot) == 0 or len(data_to_plot.columns) == 0:
                    continue

                custom_palette = {}
                for column_index, column in enumerate(data_to_plot.columns):
                    custom_palette[column] = utility.color((column_index + 1) / len(data_to_plot.columns))

                my_dashes = self.linestyles[0:len(data_to_plot.columns) - 1]

                columns_without_base = [column for column in data_to_plot.columns if column != self.base_name]
                if self.base_name in self.options.test_names:
                    sns.lineplot(data=data_to_plot[self.base_name], palette=custom_palette, linewidth=self.base_width)
                    plot = sns.lineplot(data=data_to_plot[columns_without_base], palette=custom_palette,
                                        linewidth=self.other_width,
                                        dashes=my_dashes)
                else:
                    plot = sns.lineplot(data=data_to_plot, palette=custom_palette)
                plot.set(
                    ylabel='seconds',
                    xlabel='queries')
                plot.set(yscale="linear")
                plt.title(f'{metric} over {cutoff_time} seconds')
                plt.legend(loc='upper left', borderaxespad=0)

                if metric.find('time'):
                    plt.savefig(
                        self.graph_dir + f'{metric}\\above_{cutoff_time}_seconds.svg',
                        bbox_inches='tight', dpi=600, format="svg")
                plt.close()
