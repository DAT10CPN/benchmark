import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import utility
from graph import Graph


class lines(Graph):
    def __init__(self, options):
        Graph.__init__(self, options)
        self.transformed_data = pd.DataFrame()
        self.graph_dir = super().graph_dir + '\\lines\\'
        self.linestyles = [
            [1, 1],
            [2, 2, 10, 2],
            [5, 5],
            [6, 2],
            [3, 1],
            [3, 1, 3, 1, 1, 1],
            [3, 1, 1, 1],
            [3, 5, 1, 5, 1, 5],
            [1, 1, 3, 1, 6, 1],
            [3, 1, 1, 1, 1, 1]]
        self.base_width = 3
        self.other_width = 1.5
        self.base_name = 'base'
        self.verification_memory = pd.DataFrame()
        self.state_space_size = pd.DataFrame()
        self.total_time = pd.DataFrame()
        self.verification_time = pd.DataFrame()
        self.colored_reduce_time = pd.DataFrame()
        self.unfold_time = pd.DataFrame()
        self.reduce_time = pd.DataFrame()
        self.chosen_metrics = ['verification memory']
        self.switcher = {
            'verification memory': self.verification_memory,
            'state space size': self.state_space_size,
            'total time': self.total_time,
            'verification_time': self.verification_time,
            'colored reduce time': self.colored_reduce_time,
            'unfold time': self.unfold_time,
            'reduce_time': self.reduce_time,
        }
        self.cutoff_time = [0, 0.5, 1, 5, 10, 30]
        self.keep_percentages = [0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1]
        self.name = 'lines'

    def prepare_total_time(self, cutoff_time):
        combined_df = pd.DataFrame()
        for index, data in enumerate(self.data_list):
            data = utility.remove_errors_df(data)
            res_df = pd.DataFrame()
            res_df['total time'] = data[data['answer'] != 'NONE'].apply(
                utility.get_total_time,
                axis=1)
            res_df.dropna(subset=['total time'], inplace=True)
            metric_data = ((res_df['total time'].sort_values()).reset_index()).drop(columns=
                                                                                    'index')
            metric_data = metric_data[metric_data['total time'] >= cutoff_time]
            # Rename the column to include the name of the test
            metric_data.rename(columns={'total time': self.test_names[index]}, inplace=True)

            # Either initialize or add to the combined dataframe for all csvs
            if index == 0:
                combined_df = metric_data
                continue
            combined_df = pd.concat([combined_df, metric_data], axis=1)
        combined_df.rename(utility.rename_test_name_for_paper_presentation(self.test_names), axis='columns',
                           inplace=True)
        self.total_time = combined_df

    def prepare_col_reduce_time(self, cutoff_time):
        combined_df = pd.DataFrame()
        for index, data in enumerate(self.data_list):
            data = utility.remove_errors_df(data)
            res_df = pd.DataFrame()
            res_df['colored reduce time'] = data['colored reduce time']
            res_df.dropna(subset=['colored reduce time'], inplace=True)
            metric_data = ((res_df['colored reduce time'].sort_values()).reset_index()).drop(columns=
                                                                                             'index')
            metric_data = metric_data[metric_data['colored reduce time'] >= cutoff_time]
            # Rename the column to include the name of the test
            metric_data.rename(columns={'colored reduce time': self.test_names[index]}, inplace=True)

            # Either initialize or add to the combined dataframe for all csvs
            if index == 0:
                combined_df = metric_data
                continue
            combined_df = pd.concat([combined_df, metric_data], axis=1)
        combined_df.rename(utility.rename_test_name_for_paper_presentation(self.test_names), axis='columns',
                           inplace=True)
        self.colored_reduce_time = combined_df

    def prepare_unfold_time(self, cutoff_time):
        combined_df = pd.DataFrame()
        for index, data in enumerate(self.data_list):
            data = utility.remove_errors_df(data)
            res_df = pd.DataFrame()
            res_df['unfold time'] = data['unfold time']
            res_df.dropna(subset=['unfold time'], inplace=True)
            metric_data = ((res_df['unfold time'].sort_values()).reset_index()).drop(columns=
                                                                                     'index')
            metric_data = metric_data[metric_data['unfold time'] >= cutoff_time]
            # Rename the column to include the name of the test
            metric_data.rename(columns={'unfold time': self.test_names[index]}, inplace=True)

            # Either initialize or add to the combined dataframe for all csvs
            if index == 0:
                combined_df = metric_data
                continue
            combined_df = pd.concat([combined_df, metric_data], axis=1)
        combined_df.rename(utility.rename_test_name_for_paper_presentation(self.test_names), axis='columns',
                           inplace=True)
        self.unfold_time = combined_df

    def prepare_reduce_time(self, cutoff_time):
        combined_df = pd.DataFrame()
        for index, data in enumerate(self.data_list):
            data = utility.remove_errors_df(data)
            res_df = pd.DataFrame()
            res_df['reduce time'] = data['reduce time']
            res_df.dropna(subset=['reduce time'], inplace=True)
            metric_data = ((res_df['reduce time'].sort_values()).reset_index()).drop(columns=
                                                                                     'index')
            metric_data = metric_data[metric_data['reduce time'] >= cutoff_time]
            # Rename the column to include the name of the test
            metric_data.rename(columns={'reduce time': self.test_names[index]}, inplace=True)

            # Either initialize or add to the combined dataframe for all csvs
            if index == 0:
                combined_df = metric_data
                continue
            combined_df = pd.concat([combined_df, metric_data], axis=1)
        combined_df.rename(utility.rename_test_name_for_paper_presentation(self.test_names), axis='columns',
                           inplace=True)
        self.reduce_time = combined_df

    def prepare_verification_time(self, cutoff_time):
        combined_df = pd.DataFrame()
        for index, data in enumerate(self.data_list):
            data = utility.remove_errors_df(data)
            res_df = pd.DataFrame()
            res_df['verification time'] = data[data['answer'] != 'NONE']['verification time']
            res_df.dropna(subset=['verification time'], inplace=True)
            metric_data = ((res_df['verification time'].sort_values()).reset_index()).drop(columns=
                                                                                           'index')
            metric_data = metric_data[metric_data['verification time'] >= cutoff_time]
            # Rename the column to include the name of the test
            metric_data.rename(columns={'verification time': self.test_names[index]}, inplace=True)

            # Either initialize or add to the combined dataframe for all csvs
            if index == 0:
                combined_df = metric_data
                continue
            combined_df = pd.concat([combined_df, metric_data], axis=1)
        combined_df.rename(utility.rename_test_name_for_paper_presentation(self.test_names), axis='columns',
                           inplace=True)
        self.verification_time = combined_df

    def prepare_verification_memory(self, keep_largest_percent):
        # Dataframe to hold data from all csvs
        combined_df = pd.DataFrame()
        for index, data in enumerate(self.data_list):
            data = utility.remove_errors_df(data)

            res_df = pd.DataFrame()
            res_df['verification memory'] = data[data['answer'] != 'NONE']['verification memory']
            res_df.dropna(subset=['verification memory'], inplace=True)
            metric_data = ((res_df['verification memory'].sort_values()).reset_index()).drop(columns='index')
            n = int(metric_data.shape[0] * keep_largest_percent)
            metric_data = metric_data.tail(n)
            metric_data.rename(columns={'verification memory': self.test_names[index]}, inplace=True)
            if index == 0:
                combined_df = metric_data
                continue
            combined_df = pd.concat([combined_df, metric_data], axis=1)

        combined_df.rename(utility.rename_test_name_for_paper_presentation(self.test_names), axis='columns',
                           inplace=True)
        self.verification_memory = combined_df

    def prepare_state_space_size(self, keep_largest_percent):
        # Dataframe to hold data from all csvs
        combined_df = pd.DataFrame()
        for index, data in enumerate(self.data_list):
            data = utility.remove_errors_df(data)

            res_df = data.drop(data.index[data['state space size'] == 0])
            res_df.dropna(subset=['state space size'], inplace=True)
            metric_data = ((res_df['state space size'].sort_values()).reset_index()).drop(columns='index')
            n = int(metric_data.shape[0] * keep_largest_percent)
            metric_data = metric_data.tail(n)
            metric_data.rename(columns={'state space size': self.test_names[index]}, inplace=True)
            if index == 0:
                combined_df = metric_data
                continue
            combined_df = pd.concat([combined_df, metric_data], axis=1)

        combined_df.rename(utility.rename_test_name_for_paper_presentation(self.test_names), axis='columns',
                           inplace=True)
        self.state_space_size = combined_df

    """
    def prepare_unfold_size(self):
        combined_df = pd.DataFrame()
        for index, data in enumerate(self.data_list):
            data = utility.remove_errors_df(data)
            res_df = pd.DataFrame()
            res_df[metric] = data.apply(
                utility.get_reduced_size,
                axis=1)
            res_df.dropna(subset=[metric], inplace=True)
            metric_data = ((res_df[f'{metric}'].sort_values(ascending=True)).reset_index()).drop(columns=
                                                                                                 'index')
            n = int(metric_data.shape[0] * keep_largest_percent)
            metric_data = metric_data.tail(n)
            # Rename the column to include the name of the test
            metric_data.rename(columns={f'{metric}': test_names[index]}, inplace=True)

            # Either initialize or add to the combined dataframe for all csvs
            if index == 0:
                combined_df = metric_data
                continue
            combined_df = pd.concat([combined_df, metric_data], axis=1)
        combined_df.rename(utility.rename_test_name_for_paper_presentation(self.test_names), axis='columns',
                           inplace=True)
    def prepare_col_reduced_size(self):
        combined_df = pd.DataFrame()
        for index, data in enumerate(self.data_list):
            data = utility.remove_errors_df(data)
            res_df = pd.DataFrame()
            res_df[metric] = data.apply(
                utility.get_reduced_size,
                axis=1)
            res_df.dropna(subset=[metric], inplace=True)
            metric_data = ((res_df[f'{metric}'].sort_values(ascending=True)).reset_index()).drop(columns=
                                                                                                 'index')
            n = int(metric_data.shape[0] * keep_largest_percent)
            metric_data = metric_data.tail(n)
            # Rename the column to include the name of the test
            metric_data.rename(columns={f'{metric}': test_names[index]}, inplace=True)

            # Either initialize or add to the combined dataframe for all csvs
            if index == 0:
                combined_df = metric_data
                continue
            combined_df = pd.concat([combined_df, metric_data], axis=1)
        combined_df.rename(utility.rename_test_name_for_paper_presentation(self.test_names), axis='columns',
                           inplace=True)
    def prepare_normal_reduced_size(self):
        combined_df = pd.DataFrame()
        for index, data in enumerate(self.data_list):
            data = utility.remove_errors_df(data)
            res_df = pd.DataFrame()
            res_df[metric] = data.apply(
                utility.get_reduced_size,
                axis=1)
            res_df.dropna(subset=[metric], inplace=True)
            metric_data = ((res_df[f'{metric}'].sort_values(ascending=True)).reset_index()).drop(columns=
                                                                                                 'index')
            n = int(metric_data.shape[0] * keep_largest_percent)
            metric_data = metric_data.tail(n)
            # Rename the column to include the name of the test
            metric_data.rename(columns={f'{metric}': test_names[index]}, inplace=True)

            # Either initialize or add to the combined dataframe for all csvs
            if index == 0:
                combined_df = metric_data
                continue
            combined_df = pd.concat([combined_df, metric_data], axis=1)
        combined_df.rename(utility.rename_test_name_for_paper_presentation(self.test_names), axis='columns',
                           inplace=True)"""

    def prepare_data(self):
        for cutoff_time in self.cutoff_time:
            self.prepare_total_time(cutoff_time)
            self.prepare_col_reduce_time(cutoff_time)
            self.prepare_unfold_time(cutoff_time)
            self.prepare_reduce_time(cutoff_time)
            self.prepare_verification_time(cutoff_time)
        for percentage in self.keep_percentages:
            self.prepare_verification_memory(percentage)
            self.prepare_state_space_size(percentage)
        # self.prepare_col_reduced_size()
        # self.prepare_unfold_size()
        # self.prepare_normal_reduced_size()

    def plot(self):
        sns.set_theme(style="darkgrid")

        for metric in self.chosen_metrics:
            os.makedirs(self.graph_dir + '\\lines\\' + f'\\{metric}\\')

        for cutoff_time in self.cutoff_time:
            self.plot_times(cutoff_time)
        for percentage in self.keep_percentages:
            self.plot_rest(percentage)
        # plot_ratios()

    def plot_times(self, cutoff_time):
        for metric in self.chosen_metrics:
            data_to_plot = self.switcher[metric]
            if len(data_to_plot) == 0 or len(data_to_plot.columns) == 0:
                continue

            custom_palette = {}
            for column_index, column in enumerate(data_to_plot.columns):
                custom_palette[column] = utility.color((column_index + 1) / len(data_to_plot.columns))

            my_dashes = self.linestyles[0:len(data_to_plot.columns) - 1]

            columns_without_base = [column for column in data_to_plot.columns if column != self.base_name]
            if self.base_name in self.test_names:
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
            plt.legend(loc='upper left', borderaxespad=0)

            if metric.find('time'):
                plt.savefig(
                    self.graph_dir + metric.replace(" ",
                                                    "-") + '\\' + f'{self.category}_{metric.replace(" ", "_")}_above_{cutoff_time}_seconds.svg',
                    bbox_inches='tight', dpi=600, format="svg")
            plt.close()

    """def plot_ratios(self):
        for metric in chosen_metrics:
            if metric in ["verification time", 'reduce time', 'total time']:
                unit = 'seconds'
            elif metric == 'verification memory':
                unit = 'kB'
            elif metric == 'state space size':
                unit = 'number of states'
            elif metric in ['reduced size', 'colored reduce size']:
                unit = 'ratio given by post size/pre size'
            else:
                unit = 'combined states, transitions and arcs'

            data_to_plot = switcher[metric]

            custom_palette = {}
            for column_index, column in enumerate(data_to_plot.columns):
                custom_palette[column] = utility.color((column_index + 1) / len(data_to_plot.columns))

            my_dashes = self.linestyles[0:len(data_to_plot.columns) - 1]

            columns_without_base = [column for column in data_to_plot.columns if column != self.base_name]
            # sns.set(rc={'figure.figsize': (11.7, 8.27)})
            if not (len(data_to_plot) == 0 or len(data_to_plot.columns) == 0):
                if self.base_name in self.test_names:
                    sns.lineplot(data=data_to_plot[self.base_name], palette=custom_palette, linewidth=self.base_width)
                    plot = sns.lineplot(data=data_to_plot[columns_without_base], palette=custom_palette,
                                        linewidth=self.other_width,
                                        dashes=my_dashes)
                else:
                    plot = sns.lineplot(data=data_to_plot, palette=custom_palette)
                plot.set(
                    ylabel=f'{unit}',
                    xlabel='queries')
                if metric == "reduced size":
                    plot.set(yscale="linear")
                    plt.ylim(0, 125)
                else:
                    plot.set(yscale="linear")
                plt.legend(loc='upper left', borderaxespad=0)

                if metric.find('time'):
                    plt.savefig(
                        self.graph_dir + f'{self.category}_{metric.replace(" ", "_")}_above_{cutoff_times[metric]}_seconds.svg',
                        bbox_inches='tight', dpi=600, format="svg")
                else:
                    plt.savefig(
                        self.graph_dir + f'{self.category}_{metric.replace(" ", "_")}_top_{keep_largest_percent * 100}.svg',
                        bbox_inches='tight', dpi=600, format="svg")
                plt.close()"""

    def plot_rest(self, keep_largest_percent):
        for metric in ['state space size', 'verification memory', 'unfold size']:
            if metric == 'verification memory':
                unit = 'kB'
            elif metric == 'state space size':
                unit = 'number of states'
            elif metric == 'unfold size':
                unit = 'components in net'
            else:
                unit = "ohno"

            data_to_plot = self.switcher[metric]
            if len(data_to_plot) == 0 or len(data_to_plot.columns) == 0:
                continue

            custom_palette = {}
            for column_index, column in enumerate(data_to_plot.columns):
                custom_palette[column] = utility.color((column_index + 1) / len(data_to_plot.columns))

            my_dashes = self.linestyles[0:len(data_to_plot.columns) - 1]

            columns_without_base = [column for column in data_to_plot.columns if column != self.base_name]
            if self.base_name in self.test_names:
                sns.lineplot(data=data_to_plot[self.base_name], palette=custom_palette, linewidth=self.base_width)
                plot = sns.lineplot(data=data_to_plot[columns_without_base], palette=custom_palette,
                                    linewidth=self.other_width,
                                    dashes=my_dashes)
            else:
                plot = sns.lineplot(data=data_to_plot, palette=custom_palette)
                plot.set(
                    ylabel=f'{unit}',
                    xlabel='queries')
                plot.set(yscale="linear")
                plt.legend(loc='upper left', borderaxespad=0)

            plt.savefig(
                self.graph_dir + metric.replace(" ",
                                                "-") + '\\' + f'{self.category}_{metric.replace(" ", "_")}_top_{keep_largest_percent * 100}.svg',
                bbox_inches='tight', dpi=600, format="svg")
            plt.close()
