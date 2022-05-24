import os
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import utility
from lines import Lines

warnings.filterwarnings("error")


class VerificationTimeRatio(Lines):
    def __init__(self, options):
        super().__init__(options)
        self.graph_dir = options.graph_dir + '\\ratios\\'
        self.name = 'ratios'
        self.plot_ready = pd.DataFrame()
        self.metrics_to_do_ratios = ['unfold time', 'reduce time', 'verification time',
                                     'verification memory', 'state space size']

    def prepare_data(self):
        if not self.options.base_name in self.options.test_names:
            return
        os.makedirs(self.graph_dir + "csvs")
        os.makedirs(self.graph_dir + "figs")

        for test_name in self.options.test_names:
            if test_name == self.options.base_name:
                continue
            os.makedirs(self.graph_dir + f"\\csvs\\{test_name}")

        combined = utility.combined_pd(self.data_list, self.options.test_names)
        rule_columns = [col for col in combined.columns if 'rule' in col]
        combined.drop(columns=rule_columns, inplace=True)
        for metric in self.metrics_to_do_ratios:
            for data in self.data_list:
                current_test_name = data.iloc[0]['test name']
                if current_test_name == self.options.base_name:
                    continue
                base_metric = self.options.base_name + f'@{metric}'
                current_metric = current_test_name + f'@{metric}'
                base_answer = self.options.base_name + '@answer'
                current_answer = current_test_name + '@answer'
                temp = np.where(combined[base_answer] != 'NONE',
                                np.where(combined[current_answer] != 'NONE',
                                         np.where(
                                             combined[base_metric] == combined[current_metric], 1,
                                             combined[base_metric] / combined[current_metric]),
                                         np.nan), np.nan)
                combined[f"{current_test_name}@{metric} ratio"] = temp
                curr = combined[f"{current_test_name}@{metric} ratio"].sort_values(ascending=False)

                curr.to_csv(self.graph_dir + f"csvs\\{current_test_name}\\{metric} ratio sorted.csv")
        columns_to_drop = [col for col in combined.columns if 'ratio' not in col]
        combined.drop(columns=columns_to_drop, inplace=True)
        self.plot_ready = combined
        self.plot_ready.to_csv(self.graph_dir + f'csvs\\all-ratios.csv')

    def plot(self):
        if not self.options.base_name in self.options.test_names:
            return

        for metric in self.metrics_to_do_ratios:
            relevant_columns_for_metric = [col for col in self.plot_ready.columns if metric in col]
            relevant_data = self.plot_ready[relevant_columns_for_metric].reset_index()
            relevant_data.drop(columns=['query index', 'model name'], inplace=True)
            # rename and sort
            for col in relevant_data:
                test_name = col.split("@")[0]
                relevant_data[test_name] = relevant_data[col].sort_values(ignore_index=True)
                relevant_data.drop(columns=[col], inplace=True)
            plot = self.create_lineplot(relevant_data)
            # plot.axhline(1)
            plot.set(
                ylabel='ratio',
                xlabel='queries')
            try:
                plot.set(yscale="log")
            except:
                plot.set(yscale="linear")
            plt.title(f'{self.options.base_name}-{metric}/ other tests')

            plt.savefig(
                self.graph_dir + f'figs\\{metric}.svg',
                bbox_inches='tight', dpi=600, format="svg")
            plt.close()
