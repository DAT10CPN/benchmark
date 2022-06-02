import copy
import os
import warnings
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import utility
from lines import Lines

warnings.filterwarnings("error")


class ModelRatios(Lines):
    def __init__(self, options):
        super().__init__(options)
        self.graph_dir = options.graph_dir + '\\ratios\\model-grouped\\'
        self.name = 'model-ratios'
        self.plot_ready = pd.DataFrame()
        self.metrics_to_do_ratios = ['reduce time', 'verification time', 'verification memory', 'state space size',
                                     'total time']
        if self.options.petri_net_type == 'CPN':
            self.metrics_to_do_ratios.append('unfold time')
        self.min_value = 5

    def prepare_data(self):
        if not self.options.base_name in self.options.test_names:
            return
        os.makedirs(self.graph_dir + "csvs")

        for metric in self.metrics_to_do_ratios:
            os.makedirs(self.graph_dir + f"\\csvs\\{metric}")

        orig_index = -1
        for index, test_name in enumerate(self.options.test_names):
            if test_name == self.base_name:
                orig_index = index

        all_metrics_all_experiments = pd.DataFrame()
        for metric in self.metrics_to_do_ratios:
            if metric == 'total time':
                self.options.read_results[orig_index][f"total time"] = \
                    utility.add_total_time(self.options.read_results[orig_index], self.options.petri_net_type, False)[
                        'total time']
            all_ratios_in_metric = pd.DataFrame()
            for data in self.options.read_results:

                # Get total time
                # data.set_index(["model name", "query index"], inplace=True)
                mydata = copy.deepcopy(data)
                test_name = mydata.iloc[0]['test name']

                if test_name == self.options.base_name:
                    continue
                if metric == 'total time':
                    mydata[f"total time"] = utility.add_total_time(mydata, self.options.petri_net_type, False)[
                    'total time']
                orig_and_current = utility.combined_pd([self.options.read_results[orig_index], mydata],
                                                       [self.options.base_name, test_name])
                rule_columns = [col for col in orig_and_current.columns if 'rule' in col]
                orig_and_current.drop(columns=rule_columns, inplace=True)

                orig_and_current = orig_and_current[orig_and_current[f'{self.options.base_name}@answer'] != 'NONE']
                orig_and_current = orig_and_current[orig_and_current[f'{test_name}@answer'] != 'NONE']

                orig_and_current.reset_index(inplace=True)
                orig_and_current['model name'] = orig_and_current['model name'].str.split(r'-COL').str.get(0)
                orig_and_current = orig_and_current.groupby(['model name']).sum()
                # orig_and_current.to_csv(self.graph_dir + f"{test_name}\\grouped_and_summed.csv")

                base_metric = self.options.base_name + f'@{metric}'
                current_metric = test_name + f'@{metric}'

                temp = np.where(orig_and_current[base_metric] == orig_and_current[current_metric], 1, orig_and_current[base_metric] / orig_and_current[current_metric])
                curr = pd.DataFrame()
                curr[metric] = temp.round(3)

                sorted = curr[metric].sort_values(ascending=False)
                sorted.to_csv(self.graph_dir + f"csvs\\{metric}\\{test_name} ratio sorted.csv")

                # columns_to_drop = [col for col in combined.columns if 'ratio' not in col]
                # combined.drop(columns=columns_to_drop, inplace=True)

                all_ratios_in_metric[test_name] = curr
                all_metrics_all_experiments[f"{test_name}@{metric}"] = curr
            all_ratios_in_metric.to_csv(self.graph_dir + f"csvs\\{metric}\\all.csv")
        all_metrics_all_experiments.to_csv(self.graph_dir + f"csvs\\all.csv")


    def plot(self):
        return
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
            plt.legend(loc='upper left')
            plt.savefig(
                self.graph_dir + f'figs\\{metric}.svg',
                bbox_inches='tight', dpi=600, format="svg")
            plt.close()
        # Lets first add total time column for all tests, will make it easier afterwards


"""
        combined.reset_index(inplace=True)
        combined['model name'] = combined['model name'].str.split(r'-COL').str.get(0)
        combined = combined.groupby(['model name']).sum()
        combined.to_csv(self.graph_dir + "grouped_and_summed.csv")

        for metric in self.metrics_to_do_ratios:
            for data in self.data_list:
                current_test_name = data.iloc[0]['test name']
                if current_test_name == self.options.base_name:
                    continue

                base_metric = self.options.base_name + f'@{metric}'
                current_metric = current_test_name + f'@{metric}'

                temp = combined[base_metric] / combined[current_metric]
                combined[f"{current_test_name}@{metric} ratio"] = temp
                curr = combined[f"{current_test_name}@{metric} ratio"].sort_values(ascending=False)

                curr.to_csv(self.graph_dir + f"csvs\\{current_test_name}\\{metric} ratio sorted.csv")
        columns_to_drop = [col for col in combined.columns if 'ratio' not in col]
        combined.drop(columns=columns_to_drop, inplace=True)
        self.plot_ready = combined
        self.plot_ready.to_csv(self.graph_dir + f'csvs\\all-ratios.csv')

    
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

        # Lets first add total time column for all tests, will make it easier afterwards
        for data in self.data_list:
            data.set_index(["model name", "query index"], inplace=True)
            test_name = data.iloc[0]['test name']
            combined[f"{test_name}@total time"] = utility.add_total_time(data, self.options.petri_net_type, False)[
                'total time']

        combined.reset_index(inplace=True)
        combined['model name'] = combined['model name'].str.split(r'-COL').str.get(0)
        combined = combined.groupby(['model name']).sum()
        combined.to_csv(self.graph_dir + "grouped_and_summed.csv")

        for metric in self.metrics_to_do_ratios:
            for data in self.data_list:
                current_test_name = data.iloc[0]['test name']
                if current_test_name == self.options.base_name:
                    continue

                base_metric = self.options.base_name + f'@{metric}'
                current_metric = current_test_name + f'@{metric}'

                temp = combined[base_metric] / combined[current_metric]
                combined[f"{current_test_name}@{metric} ratio"] = temp
                curr = combined[f"{current_test_name}@{metric} ratio"].sort_values(ascending=False)

                curr.to_csv(self.graph_dir + f"csvs\\{current_test_name}\\{metric} ratio sorted.csv")
        columns_to_drop = [col for col in combined.columns if 'ratio' not in col]
        combined.drop(columns=columns_to_drop, inplace=True)
        self.plot_ready = combined
        self.plot_ready.to_csv(self.graph_dir + f'csvs\\all-ratios.csv')
"""
