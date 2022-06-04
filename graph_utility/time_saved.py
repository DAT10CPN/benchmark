import os
import warnings

import pandas as pd

import utility
from lines import Lines

warnings.filterwarnings("error")


class TimeSaved(Lines):
    def __init__(self, options):
        super().__init__(options)
        self.graph_dir = options.graph_dir + '\\time_saved\\'
        self.name = 'time-saved'
        self.plot_ready = pd.DataFrame()
        os.makedirs(self.graph_dir)
        self.metrics_to_do_saved = ['verification time', 'total time', 'reduce time', 'unfold time']

    def prepare_data(self):
        combined = utility.combined_pd(self.data_list, self.options.test_names)
        rule_columns = [col for col in combined.columns if 'rule' in col]
        combined.drop(columns=rule_columns, inplace=True)

        # Lets first add total time column for all tests, will make it easier afterwards
        for data in self.data_list:
            data.set_index(["model name", "query index"], inplace=True)
            test_name = data.iloc[0]['test name']
            combined[f"{test_name}@total time"] = utility.add_total_time(data, self.options.petri_net_type, False)[
                'total time']

        total_time_saved = pd.DataFrame()
        total_time_saved_percentage = pd.DataFrame()
        total_time_saved_per_model = pd.DataFrame()
        for data in self.data_list:
            current_test_name = data.iloc[0]['test name']
            if current_test_name == self.options.base_name:
                continue

            comparison = combined[combined[f'{self.options.base_name}@answer'] != 'NONE']
            comparison = comparison[comparison[f'{current_test_name}@answer'] != 'NONE']

            sums = comparison.sum()

            model_sums = comparison
            model_sums.reset_index(inplace=True)
            if self.options.petri_net_type == 'CPN':
                model_sums['model name'] = model_sums['model name'].str.split(r'-COL').str.get(0)
            else:
                model_sums['model name'] = model_sums['model name'].str.split(r'-PT').str.get(0)
            model_sums = model_sums.groupby(['model name']).sum()

            temp = pd.DataFrame()
            model_temp = pd.DataFrame()
            percentage_temp = pd.DataFrame()
            for metric in self.metrics_to_do_saved:
                base_metric = self.options.base_name + f'@{metric}'
                current_metric = current_test_name + f'@{metric}'

                model_temp[f"{current_test_name}_{metric}"] = model_sums[current_metric] - model_sums[base_metric]
                temp[metric] = pd.Series(sums[base_metric] - sums[current_metric])
                percentage_temp[metric] = pd.Series(sums[current_metric] / sums[base_metric])
            total_time_saved[current_test_name] = temp.T
            total_time_saved_percentage[current_test_name] = percentage_temp.T
            if len(total_time_saved_per_model) == 0:
                total_time_saved_per_model = model_temp
            else:
                total_time_saved_per_model = total_time_saved_per_model.merge(model_temp, left_index=True, right_index=True)

        total_time_saved_percentage.round(3).to_csv(self.graph_dir + f'time_saved_all_percentage.csv')
        total_time_saved.round(3).to_csv(self.graph_dir + f'time_saved_all.csv')
        total_time_saved_per_model.round(3).to_csv(self.graph_dir + f'time_saved_all_per_model.csv')

    def plot(self):
        pass
