import os

import matplotlib.pyplot as plt
import pandas as pd

import utility
from lines import Lines


class MemoryStateLines(Lines):
    def __init__(self, options):
        super().__init__(options)
        self.name = 'memory-state lines'
        self.verification_memories = []
        self.state_space_sizes = []

    def prepare_data(self):
        for metric in ['state space size', 'verification memory']:
            os.makedirs(self.graph_dir + f'\\{metric}\\')

        for keep_percentage in self.keep_percentages:
            for metric in ['state space size', 'verification memory']:
                combined_df = pd.DataFrame()
                for index, data in enumerate(self.data_list):
                    data = data.drop(data[data['error'] <= 4].index)

                    if len(data) == 0:
                        print(
                            f"Test full of error 4 or lower, so graphs cannot be made for metric ({metric}) in class ({self.name}). Check the errors in: {self.options.test_names[index]}")
                        continue
                    res_df = pd.DataFrame()
                    if metric == 'state space size':
                        res_df = data.drop(data.index[data['state space size'] == 0])
                    res_df[metric] = data[data['answer'] != 'NONE'][metric]
                    res_df.dropna(subset=[metric], inplace=True)
                    metric_data = ((res_df[metric].sort_values()).reset_index()).drop(columns='index')
                    n = int(metric_data.shape[0] * keep_percentage)
                    metric_data = metric_data.tail(n)
                    metric_data.rename(columns={metric: self.options.test_names[index]}, inplace=True)
                    if index == 0:
                        combined_df = metric_data
                        continue
                    combined_df = pd.concat([combined_df, metric_data], axis=1)
                if metric == 'verification memory':
                    self.verification_memories.append(combined_df)
                elif metric == 'state space size':
                    self.state_space_sizes.append(combined_df)

    def plot(self):
        for index, percentage in enumerate(self.keep_percentages):
            for metric in ['state space size', 'verification memory']:
                if metric == 'verification memory':
                    unit = 'kB'
                    data_to_plot = self.verification_memories[index]
                elif metric == 'state space size':
                    unit = 'number of states'
                    data_to_plot = self.state_space_sizes[index]
                else:
                    raise Exception("Something went wrong in lines memory state")

                plot = self.create_lineplot_highlight_orig(data_to_plot)

                plot.set(
                    ylabel=f'{unit}',
                    xlabel='queries')
                try:
                    plot.set(yscale="log")
                except:
                    plot.set(yscale="linear")
                #plt.legend(labels=utility.get_col_names(data_to_plot.columns), loc='upper left', borderaxespad=0)
                plt.title(f"top {percentage * 100}% largest {metric}")
                plt.savefig(
                    self.graph_dir + f'{metric}\\top_{percentage * 100}%.svg',
                    bbox_inches='tight', dpi=600, format="svg")
                plt.close()
