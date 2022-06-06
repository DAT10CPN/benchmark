import copy
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
        self.metrics_to_do_saved = ['verification time', 'total time', 'reduce time', 'state space size',
                                    'reduced size']
        if options.petri_net_type == 'CPN':
            cpn_metrics = ['unfold time', 'color reduce size', 'unfold size']
            for cpn_metric in cpn_metrics:
                self.metrics_to_do_saved.append(cpn_metric)

    def get_common(self, combined, metric, current_test_name):
        df = copy.deepcopy(combined)
        if metric == 'answer':
            common_rows = df[df[f'{self.options.base_name}@{metric}'] != 'NONE']
            common_rows = common_rows[common_rows[f'{current_test_name}@{metric}'] != 'NONE']
        else:
            common_rows = df[df[f'{self.options.base_name}@{metric}'] > 0]
            common_rows = common_rows[common_rows[f'{current_test_name}@{metric}'] > 0]
        colomns_to_drop = [col for col in common_rows.columns if
                           (((self.options.base_name in col) or (current_test_name in col)) and (
                               not metric in col)) or (not current_test_name in col) and (
                               not self.options.base_name in col)]
        common_rows.drop(columns=colomns_to_drop, inplace=True)
        common_rows.reset_index(inplace=True)
        return common_rows

    def sum_by_model_name(self, df):
        model_sums = copy.deepcopy(df)
        model_sums.reset_index(inplace=True)
        if self.options.petri_net_type == 'CPN':
            model_sums['model name'] = model_sums['model name'].str.replace(r'-COL.*', "", regex=True)
        else:
            model_sums['model name'] = model_sums['model name'].str.replace(r'-PT*', "", regex=True)
        model_sums = model_sums.groupby(['model name']).sum()
        return model_sums

    def get_individual_model_query_comparisons(self, common_answers, metric, current_test_name):
        base_metric = self.options.base_name + f'@{metric}'
        current_metric = current_test_name + f'@{metric}'
        metric_compare = pd.DataFrame()

        # All the individual model+query comparisons
        metric_compare["model name"] = common_answers["model name"]
        metric_compare["query index"] = common_answers["query index"]
        metric_compare["base"] = common_answers[base_metric]
        metric_compare[current_test_name] = common_answers[current_metric]
        metric_compare["diff"] = common_answers[base_metric] - common_answers[
            current_metric]
        metric_compare["diff %"] = common_answers[current_metric] / common_answers[
            base_metric]
        return metric_compare

    def get_summed_model_comparisons(self, common_answers_summed, metric, current_test_name):
        base_metric = self.options.base_name + f'@{metric}'
        current_metric = current_test_name + f'@{metric}'
        metric_compare_sum_by_model_name = pd.DataFrame()
        metric_compare_sum_by_model_name["base"] = common_answers_summed[base_metric]
        metric_compare_sum_by_model_name[current_test_name] = common_answers_summed[current_metric]
        metric_compare_sum_by_model_name["diff"] = common_answers_summed[base_metric] - common_answers_summed[
            current_metric]
        metric_compare_sum_by_model_name["diff %"] = common_answers_summed[current_metric] / common_answers_summed[
            base_metric]
        return metric_compare_sum_by_model_name

    def individual_comparisons(self, common_answers_rows, metric, current_test_name):
        metric_compare = self.get_individual_model_query_comparisons(common_answers_rows, metric,
                                                                     current_test_name)
        metric_compare_filtered = self.filter_by_time_and_sort(metric_compare, metric)
        metric_compare_filtered.to_csv(self.graph_dir + f"{current_test_name}\\{metric}-individual.csv")
        metric_compare_with_index = copy.deepcopy(metric_compare)
        metric_compare_with_index.set_index(['model name', 'query index'], inplace=True)
        return pd.DataFrame(metric_compare_with_index['diff'])

    def filter_by_time_and_sort(self, df, metric):
        df = copy.deepcopy(df)
        if 'time' in metric:
            df = df[df['base'] > 2]
        df = df.sort_values(by='diff %', ascending=True).round(3)
        return df

    def model_summed_comparisons(self, common_answers_rows, metric, current_test_name):
        common_answers_summed_by_models = self.sum_by_model_name(common_answers_rows)
        metric_compare_sum_by_model_name = self.get_summed_model_comparisons(common_answers_summed_by_models,
                                                                             metric, current_test_name)
        metric_compare_sum_by_model_name_filtered = self.filter_by_time_and_sort(metric_compare_sum_by_model_name,
                                                                                 metric)
        metric_compare_sum_by_model_name_filtered.to_csv(self.graph_dir + f"{current_test_name}\\{metric}-grouped.csv")
        return pd.DataFrame(metric_compare_sum_by_model_name['diff'])

    def prepare_data(self):
        combined = utility.combined_pd(self.data_list, self.options.test_names)
        rule_columns = [col for col in combined.columns if 'rule' in col]
        combined.drop(columns=rule_columns, inplace=True)

        # Lets first add the calculated columns for all data, will make it easier afterwards
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

        data_metric_pd_map = {}
        data_metric_sum_pd_map = {}
        for metric in self.metrics_to_do_saved:
            metric_all_experiments = pd.DataFrame()
            metric_all_experiments_summed = pd.DataFrame()

            data_metric_pd_map[metric] = metric_all_experiments
            data_metric_sum_pd_map[metric] = metric_all_experiments_summed

        for data in self.data_list:
            current_test_name = data.iloc[0]['test name']
            if current_test_name == self.options.base_name:
                continue

            os.makedirs(self.graph_dir + current_test_name)

            all_metric_for_this_experiment_individual = pd.DataFrame()
            all_metric_for_this_experiment_sum = pd.DataFrame()
            for metric in self.metrics_to_do_saved:
                common_answers_rows = self.get_common(combined, metric, current_test_name)
                individual_comparison = self.individual_comparisons(common_answers_rows, metric,
                                                                    current_test_name).round(2)
                sum_comparison = self.model_summed_comparisons(common_answers_rows, metric, current_test_name).round(2)

                individual_comparison.rename(columns={'diff': metric}, inplace=True)
                sum_comparison.rename(columns={'diff': metric}, inplace=True)

                all_metric_for_this_experiment_individual = pd.concat(
                    [all_metric_for_this_experiment_individual, individual_comparison], axis=1)
                all_metric_for_this_experiment_sum = pd.concat([all_metric_for_this_experiment_sum, sum_comparison],
                                                               axis=1)

                individual_comparison.rename(columns={metric: current_test_name}, inplace=True)
                sum_comparison.rename(columns={metric: current_test_name}, inplace=True)

                data_metric_pd_map[metric] = pd.concat(
                    [data_metric_pd_map[metric], individual_comparison], axis=1)
                # data_metric_sum_pd_map[metric] = pd.concat(
                #   [data_metric_sum_pd_map[metric], sum_comparison], axis=1)

            all_metric_for_this_experiment_sum.to_csv(self.graph_dir + f"{current_test_name}\\all_metrics_grouped.csv")
            all_metric_for_this_experiment_individual.to_csv(
                self.graph_dir + f"{current_test_name}\\all_metrics_individual.csv")

        for metric in self.metrics_to_do_saved:
            data_metric_pd_map[metric].to_csv(self.graph_dir + f"by_metric\\{metric}_individual.csv")
            data_metric_sum_pd_map[metric].to_csv(self.graph_dir + f"by_metric\\{metric}_grouped.csv")

        # for metric in self.metrics_to_do_saved:
        # for col in with_removed_cols.columns:
        #    with_removed_cols[col] = np.where((np.abs(with_removed_cols[col]) < 10), np.nan,
        #                                      with_removed_cols[col])
        # for col in with_removed_cols.columns:
        # with_removed_cols[col] = np.where((np.isnan(with_removed_cols[col])), "-",
        # with_removed_cols[col])
        #    with_removed_cols.rename(columns={col: col.split(rf'_{metric}')[0]}, inplace=True)
        # with_removed_cols.to_csv(self.graph_dir + f'{metric}_per_model.csv')
        # latex = with_removed_cols.to_latex(index=True)
        # with open(self.graph_dir + f"\\time_saved_all_per_model_{metric}.tex", mode='w') as file:
        #  file.write(latex)

    def plot(self):
        pass
