import copy
import os
import warnings

import pandas as pd
import numpy as np
import utility
from lines import Lines

warnings.filterwarnings("error")


class ModelRatiosAverages(Lines):
    def __init__(self, options):
        super().__init__(options)
        self.graph_dir = options.graph_dir + '\\ratios\\model-grouped-average\\'
        self.name = 'model-ratios-average'
        self.plot_ready = pd.DataFrame()
        self.metrics_to_do_ratios = ['reduce time', 'verification time', 'verification memory', 'state space size',
                                     'total time']
        if self.options.petri_net_type == 'CPN':
            self.metrics_to_do_ratios.append('unfold time')

    def prepare_data(self):
        if not self.options.base_name in self.options.test_names:
            return
        os.makedirs(self.graph_dir)

        for metric in self.metrics_to_do_ratios:
            os.makedirs(self.graph_dir + f"{metric}")

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

                base_metric = self.options.base_name + f'@{metric}'
                current_metric = test_name + f'@{metric}'
                orig_and_current['ratio'] = orig_and_current[base_metric] / orig_and_current[current_metric]

                def get_ratio(row):
                    if row[base_metric] == row[current_metric]:
                        return 1
                    elif row[current_metric] == 0 and metric == 'verification time':
                        return (row[base_metric] + 0.1) / 0.1
                    elif row[base_metric] < 2 and row[current_metric] < 2:
                        return 1
                    elif row[current_metric] == 0:
                        return np.nan
                    else:
                        return row[base_metric] / row[current_metric]
                orig_and_current['ratio'] = orig_and_current.apply( lambda row:
                    get_ratio(row), axis=1)

                temp = orig_and_current.groupby(['model name']).mean()

                # orig_and_current.to_csv(self.graph_dir + f"{test_name}\\grouped_and_summed.csv")

                curr = pd.DataFrame()
                curr[metric] = temp['ratio'].round(3)

                sorted = curr[metric].sort_values(ascending=False)
                sorted.to_csv(self.graph_dir + f"{metric}\\{test_name} ratio sorted.csv")

                # columns_to_drop = [col for col in combined.columns if 'ratio' not in col]
                # combined.drop(columns=columns_to_drop, inplace=True)

                all_ratios_in_metric[test_name] = curr
                all_metrics_all_experiments[f"{test_name}@{metric}"] = curr
            all_ratios_in_metric.to_csv(self.graph_dir + f"{metric}\\all.csv")
        all_metrics_all_experiments.to_csv(self.graph_dir + f"all.csv")
