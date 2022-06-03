import numpy as np
import seaborn as sns

import utility
from graph import Graph


class Lines(Graph):
    def __init__(self, options):
        super().__init__(options)
        self.graph_dir = options.graph_dir + '\\lines\\'
        self.linestyles = [[1, 1],
                           [2, 2, 10, 2],
                           [5, 5],
                           [6, 2],
                           [3, 1],
                           [3, 1, 3, 1, 1, 1],
                           [3, 1, 1, 1],
                           [3, 4, 2, 4, 2, 4],
                           [1, 1, 3, 1, 6, 1],
                           [3, 1, 1, 1, 1, 1],
                           ] * 3
        self.base_width = 2.25
        self.other_width = 1.5
        self.base_name = self.options.base_name
        self.base_color = np.array([0.1, 0.1, 0.1])
        if self.options.enable_graphs == 1:
            self.cutoff_times = [3, 30]
            self.keep_percentages = [0.05, 0.15]
        elif self.options.enable_graphs == 2:
            self.cutoff_times = [0, 2.5, 5, 12, 30, 60]
            self.keep_percentages = [0.01, 0.05, 0.12, 0.25, 0.8]

    def create_lineplot_highlight_orig(self, data_to_plot):
        custom_palette = {}
        for column_index, column in enumerate(data_to_plot.columns):
            if (column == self.base_name):
                custom_palette[column] = self.base_color
                continue
            custom_palette[column] = utility.color((column_index + 1) / len(data_to_plot.columns))

        my_dashes = self.linestyles[0:len(data_to_plot.columns) - 1]
        columns_without_base = [column for column in data_to_plot.columns if column != self.base_name]
        if self.base_name in self.options.test_names:
            sns.lineplot(data=data_to_plot[[self.base_name]], palette=custom_palette, linewidth=self.base_width)
            plot = sns.lineplot(data=data_to_plot[columns_without_base], palette=custom_palette,
                                linewidth=self.other_width,
                                dashes=my_dashes)
        else:
            plot = sns.lineplot(data=data_to_plot, palette=custom_palette)

        return plot

    def create_lineplot(self, data_to_plot):
        custom_palette = {}
        for column_index, column in enumerate(data_to_plot.columns):
            custom_palette[column] = utility.color((column_index + 1) / len(data_to_plot.columns))
        plot = sns.lineplot(data=data_to_plot, palette=custom_palette)

        return plot
