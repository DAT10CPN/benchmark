import os
from collections import defaultdict
from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import utility
from lines import Lines


@dataclass()
class TimeMetric:
    line_metric_name: str
    is_in_phase: int


class TimeLines(Lines):
    def __init__(self, options):
        super().__init__(options)
        self.name = 'time lines'
        self.times = defaultdict(dict)
        self.time_metrics = [
            TimeMetric(
                line_metric_name='reduce time',
                is_in_phase=3
            ),
            TimeMetric(
                line_metric_name='verification time',
                is_in_phase=4
            ),
            TimeMetric(
                line_metric_name='total time',
                is_in_phase=4
            )
        ]
        if options.petri_net_type == 'cpn':
            self.time_metrics.append([
                TimeMetric(
                    line_metric_name='colored reduce time',
                    is_in_phase=1
                ),
                TimeMetric(
                    line_metric_name='unfold time',
                    is_in_phase=2
                )])

    def prepare_data(self):
        for metric in self.time_metrics:
            os.makedirs(self.graph_dir + f'\\{metric.line_metric_name}\\')

        for metric in self.time_metrics:
            for cutoff_time in self.cutoff_times:
                combined_df = pd.DataFrame()
                for index, data in enumerate(self.data_list):

                    data = data.drop(data[data['error'] <= metric.is_in_phase].index)
                    if len(data) == 0:
                        print(
                            f"Test full of error {metric.is_in_phase} or lower, so graphs cannot be made for metric ({metric.line_metric_name}) in class ({self.name}). Check the errors in: {self.options.test_names[index]}")
                        continue
                    res_df = pd.DataFrame()
                    if metric.line_metric_name == 'total time':
                        if self.options.petri_net_type == 'CPN':
                            res_df['total time'] = data[data['answer'] != 'NONE'].apply(
                                utility.cpn_get_total_time,
                                axis=1)
                        elif self.options.petri_net_type == 'PT':
                            res_df['total time'] = data[data['answer'] != 'NONE'].apply(
                                utility.pt_get_total_time,
                                axis=1)
                    else:
                        res_df[metric.line_metric_name] = data[metric.line_metric_name]

                    res_df.dropna(subset=[metric.line_metric_name], inplace=True)
                    metric_data = ((res_df[metric.line_metric_name].sort_values()).reset_index()).drop(columns='index')
                    metric_data = metric_data[metric_data[metric.line_metric_name] >= cutoff_time]
                    # Rename the column to include the name of the test
                    metric_data.rename(columns={metric.line_metric_name: self.options.test_names[index]}, inplace=True)

                    # Either initialize or add to the combined dataframe for all csvs
                    if index == 0:
                        combined_df = metric_data
                        continue
                    combined_df = pd.concat([combined_df, metric_data], axis=1)
                self.times[metric.line_metric_name][cutoff_time] = combined_df

    def plot(self):
        sns.set_theme(style="darkgrid")
        for cutoff_time in self.cutoff_times:
            for metric in self.time_metrics:
                data_to_plot = self.times[metric.line_metric_name][cutoff_time]

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
                try:
                    plot.set(yscale="log")
                except:
                    plot.set(yscale="linear")
                plt.title(f'{metric.line_metric_name} over {cutoff_time} seconds')
                plt.legend(loc='upper left', borderaxespad=0)

                plt.savefig(
                    self.graph_dir + f'{metric.line_metric_name}\\above_{cutoff_time}_seconds.svg',
                    bbox_inches='tight', dpi=600, format="svg")
                plt.close()
