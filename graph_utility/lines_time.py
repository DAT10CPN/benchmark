import os
from collections import defaultdict
from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd

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
        if options.petri_net_type == 'CPN':
            self.time_metrics.append(
                TimeMetric(
                    line_metric_name='colored reduce time',
                    is_in_phase=1
                ))
            self.time_metrics.append(
                TimeMetric(
                    line_metric_name='unfold time',
                    is_in_phase=2
                ))

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
                        res_df = utility.add_total_time(data, self.options.petri_net_type, True)
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
        for cutoff_time in self.cutoff_times:
            for metric in self.time_metrics:
                data_to_plot = self.times[metric.line_metric_name][cutoff_time]

                plot = self.create_lineplot_highlight_orig(data_to_plot)
                plot.set(
                    ylabel='seconds',
                    xlabel='queries')
                try:
                    plot.set(yscale="log")
                except:
                    plot.set(yscale="linear")
                plt.title(f'{metric.line_metric_name} over {cutoff_time} seconds')
                #plt.legend(labels=utility.get_col_names(data_to_plot.columns), loc='upper left', borderaxespad=0)
                plt.legend(loc='upper left')
                plt.savefig(
                    self.graph_dir + f'{metric.line_metric_name}\\above_{cutoff_time}_seconds.svg',
                    bbox_inches='tight', dpi=600, format="svg")
                plt.close()
