import pandas as pd
import utility
from lines import Lines
import seaborn as sns
import matplotlib.pyplot as plt

class RatioLines(Lines):
    def __init__(self, options):
        super().__init__(options)


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
                           inplace=True)

    def prepare_data(self):
        self.prepare_col_reduced_size()
        self.prepare_unfold_size()
        self.prepare_normal_reduced_size()

    def plot_ratios(self):
        for metric in chosen_metrics:
            if metric in ['reduced size', 'colored reduce size']:
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
                plt.close()

    def plot(self):
        sns.set_theme(style="darkgrid")

        self.plot_ratios()

