import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import utility
from lines import Lines


class SizeLines(Lines):
    def __init__(self, options):
        super().__init__(options)
        self.size_metrics = [
            ['color reduced size', ['colored reduce place count', 'colored reduce transition count']],
            ['unfolded size', ['unfolded place count', 'unfolded transition count']],
            ['reduced size', ['reduced place count', 'reduced transition count']]
        ]
        self.computed_sizes = {}
        self.name = 'size lines'

        #for metric_name in [metric[0] for metric in self.size_metrics]:
        #    os.makedirs(self.graph_dir + f'\\{metric_name}\\')

    def prepare_data(self):
        for metric in self.size_metrics:
            metric_name = metric[0]
            combined_df = pd.DataFrame()
            for index, data in enumerate(self.data_list):
                data = utility.remove_errors_df(data)
                res_df = pd.DataFrame()

                columns_list = metric[1]
                res_df[metric_name] = data[columns_list].sum(axis=1)
                res_df.dropna(subset=[metric_name], inplace=True)
                metric_data = ((res_df[f'{metric_name}'].sort_values(ascending=True)).reset_index()).drop(columns=
                                                                                                          'index')
                # Rename the column to include the name of the test
                metric_data.rename(columns={f'{metric_name}': self.options.test_names[index]}, inplace=True)

                # Either initialize or add to the combined dataframe for all csvs
                if index == 0:
                    combined_df = metric_data
                    continue
                combined_df = pd.concat([combined_df, metric_data], axis=1)
            # combined_df.rename(utility.rename_test_name_for_paper_presentation(self.test_names), axis='columns',
            # inplace=True)
            self.computed_sizes[metric_name] = combined_df

    def plot(self):
        sns.set_theme(style="darkgrid")
        for metric in self.size_metrics:
            metric_name = metric[0]

            data_to_plot = self.computed_sizes[metric_name]

            custom_palette = {}
            for column_index, column in enumerate(data_to_plot.columns):
                custom_palette[column] = utility.color((column_index + 1) / len(data_to_plot.columns))

            my_dashes = self.linestyles[0:len(data_to_plot.columns) - 1]

            columns_without_base = [column for column in data_to_plot.columns if column != self.base_name]
            if not (len(data_to_plot) == 0 or len(data_to_plot.columns) == 0):
                if self.base_name in self.options.test_names:
                    sns.lineplot(data=data_to_plot[self.base_name], palette=custom_palette, linewidth=self.base_width)
                    plot = sns.lineplot(data=data_to_plot[columns_without_base], palette=custom_palette,
                                        linewidth=self.other_width,
                                        dashes=my_dashes)
                else:
                    plot = sns.lineplot(data=data_to_plot, palette=custom_palette)
                plot.set(
                    ylabel=f'Combined number of transition and places',
                    xlabel='queries')
                plot.set(yscale="linear")
                plt.legend(loc='upper left', borderaxespad=0)

                plt.savefig(
                    self.graph_dir + f'{metric_name}.svg',
                    bbox_inches='tight', dpi=600, format="svg")
                plt.close()
