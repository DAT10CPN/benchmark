import os
import warnings

import numpy as np
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
        self.metrics_to_do_saved = ['verification time', 'total time', 'reduce time', 'state space size',
                                    'reduced size']
        if options.petri_net_type == 'CPN':
            cpn_metrics = ['unfold time', 'color reduce size', 'unfold size']
            for cpn_metric in cpn_metrics:
                self.metrics_to_do_saved.append(cpn_metric)

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

            combined[f"{test_name}@reduced size"] = data.apply(
                utility.get_reduced_size,
                axis=1)
            if self.options.petri_net_type == 'CPN':
                combined[f"{test_name}@color reduce size"] = data.apply(
                    utility.get_colored_reduced_size,
                    axis=1)

                combined[f"{test_name}@unfold size"] = data.apply(
                    utility.get_unfolded_size,
                    axis=1)

        total_time_saved_per_model = pd.DataFrame()
        for data in self.data_list:
            current_test_name = data.iloc[0]['test name']
            if current_test_name == self.options.base_name:
                continue

            comparison = combined[combined[f'{self.options.base_name}@answer'] != 'NONE']
            comparison = comparison[comparison[f'{current_test_name}@answer'] != 'NONE']

            comparison_sps = combined[combined[f'{self.options.base_name}@state space size'] > 0]
            comparison_sps = comparison_sps[comparison_sps[f'{current_test_name}@state space size'] > 0]

            model_sums = comparison
            model_sums.reset_index(inplace=True)
            model_sums_sps = comparison_sps
            model_sums_sps.reset_index(inplace=True)
            if self.options.petri_net_type == 'CPN':
                model_sums['model name'] = model_sums['model name'].str.replace(r'-COL.*', "", regex=True)
                model_sums_sps['model name'] = model_sums_sps['model name'].str.replace(r'-COL.*', "", regex=True)
            else:
                model_sums['model name'] = model_sums['model name'].str.replace(r'-PT*', "", regex=True)
                model_sums_sps['model name'] = model_sums_sps['model name'].str.replace(r'-PT*', "", regex=True)
            model_sums = model_sums.groupby(['model name']).sum()
            model_sums_sps = model_sums_sps.groupby(['model name']).sum()

            model_temp = pd.DataFrame()
            for metric in self.metrics_to_do_saved:
                base_metric = self.options.base_name + f'@{metric}'
                current_metric = current_test_name + f'@{metric}'

                if metric == 'state space size':
                    model_temp[f"{current_test_name}_{metric}"] = model_sums_sps[base_metric] - model_sums_sps[current_metric]
                else:
                    model_temp[f"{current_test_name}_{metric}"] = model_sums[base_metric] - model_sums[current_metric]
            if len(total_time_saved_per_model) == 0:
                total_time_saved_per_model = model_temp
            else:
                total_time_saved_per_model = total_time_saved_per_model.merge(model_temp, left_index=True,
                                                                              right_index=True)

        total_time_saved_per_model.round(3).to_csv(self.graph_dir + f'time_saved_all_per_model.csv')

        for metric in self.metrics_to_do_saved:
            # do the just total time, with small values removed
            irrelevant_columns = [col for col in total_time_saved_per_model.columns if not metric in col]
            with_removed_cols = total_time_saved_per_model.drop(columns=irrelevant_columns)
            #for col in with_removed_cols.columns:
            #    with_removed_cols[col] = np.where((np.abs(with_removed_cols[col]) < 10), np.nan,
            #                                      with_removed_cols[col])
            with_removed_cols = with_removed_cols.round(5)
            for col in with_removed_cols.columns:
                #with_removed_cols[col] = np.where((np.isnan(with_removed_cols[col])), "-",
                                                  #with_removed_cols[col])
                with_removed_cols.rename(columns={col: col.split(rf'_{metric}')[0]}, inplace=True)
            with_removed_cols.to_csv(self.graph_dir + f'{metric}_per_model.csv')
            #latex = with_removed_cols.to_latex(index=True)
            #with open(self.graph_dir + f"\\time_saved_all_per_model_{metric}.tex", mode='w') as file:
              #  file.write(latex)

    def plot(self):
        pass
