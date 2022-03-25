import os
import re
import warnings

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from graph import Graph

warnings.filterwarnings("error")


class RuleUsage(Graph):
    def __init__(self, options):
        super().__init__(options)
        self.transformed_data = pd.DataFrame()
        self.rules_summed = []
        self.percentages = []
        self.models_using_rule = []
        self.all_percentages = pd.DataFrame()
        self.new_test_names = []
        self.graph_dir = options.graph_dir + '\\rules\\'
        self.name = 'rules'

        os.makedirs(self.graph_dir)
        for test_name in self.options.test_names:
            os.makedirs(self.graph_dir + f'\\{test_name}\\')
        for graph_type in ['absolute applications', 'absolute models', 'percentage models']:
            os.makedirs(self.graph_dir + f'\\{graph_type}\\')

    def prepare_data(self):

        # Make one plot (png) for each csv
        for test_index, data in enumerate(self.data_list):

            data.drop(data[data['error'] <= 3].index, inplace=True)
            # Find rule names
            rules = [column for column in data.columns.tolist() if
                     "rule" in column]

            # Sum over all rows the number of times each rule has been used
            rules_summed = data[rules].agg('sum').to_frame().T

            data_grouped_by_model = data.groupby(['model name'])[rules].agg('sum')
            percentages = (((((data_grouped_by_model > 0) * 1).mean()) * 100).to_frame()).T

            models_using_rule = ((data_grouped_by_model > 0) * 1).agg('sum').to_frame().T

            # Remove the 'Rule' part of e.g 'Rule A'
            for df in [rules_summed, percentages, models_using_rule]:
                df.rename(columns=lambda x: re.sub('rule', '', x), inplace=True)

            self.models_using_rule.append(models_using_rule)
            self.percentages.append(percentages)
            self.rules_summed.append(rules_summed)
            # self.new_test_names.append(new_test_name)
            self.new_test_names.append(self.options.test_names[test_index])

    def plot(self):
        sns.set_theme(style="darkgrid", palette="pastel")
        # Plot the plots
        self.plot_rules_summed()
        self.plot_percentages()
        self.plot_models_using_rule()

    def plot_rules_summed(self):
        for i in range(len(self.options.test_names)):
            plot = sns.barplot(data=self.rules_summed[i])
            try:
                plot.set_yscale("log")
            except:
                print(
                    f"Test has probably gone wrong, had no application of any rules: {self.options.test_names[i]}.csv")
                plot.set_yscale("linear")
            plot.set(title=f'{self.new_test_names[i]} number of times rules are used', ylabel='uses', xlabel='rules')
            # This for-loop puts the number of times each rule has been used, on top of the bar
            for p in plot.patches:
                plot.annotate(format(p.get_height().astype(int), 'd'),
                              ((p.get_x() + p.get_width() / 2).astype(int), p.get_height().astype(int)),
                              ha='center', va='center',
                              size=12,
                              xytext=(0, 8),
                              textcoords='offset points')

            self.save_fig(self.options.test_names[i], 'absolute applications')
            plt.clf()

    def plot_percentages(self):
        # Plot the plot
        for i in range(len(self.options.test_names)):
            plot = sns.barplot(data=self.percentages[i])
            plot.set(title=f'{self.new_test_names[i]} percentage of models using rules', ylabel='uses in %',
                     xlabel='rules')
            # Plots numbers above bars
            for p in plot.patches:
                if p.get_height() != 0.0:
                    plot.annotate(format(p.get_height(), '.1f'),
                                  (p.get_x() + p.get_width() / 2.,
                                   p.get_height()),
                                  ha='center', va='center',
                                  size=12,
                                  xytext=(0, 8),
                                  textcoords='offset points')

            self.save_fig(self.options.test_names[i], 'percentage models')
            plt.clf()

            # todo, might not needed, was for big table in last paper of rule applications
            # self.percentages[i].rename(index={
            #    0: utility.rename_test_name_for_paper_presentation(self.test_names)[self.test_names[i]].replace("⃰",
            #                                                                                                    "*")},
            #   inplace=True)
            # self.percentages[i].drop([' J', ' K'], axis=1, inplace=True)
            # self.percentages[i] = self.percentages[i].round(1)
            # self.all_percentages = self.all_percentages.append(self.percentages[i])

    def plot_models_using_rule(self):
        for i in range(len(self.options.test_names)):
            plot = sns.barplot(data=self.models_using_rule[i])
            plot.set(title=f'{self.new_test_names[i]} number of models using rules', ylabel='uses', xlabel='rules')
            # Plots numbers above bars
            for p in plot.patches:
                if p.get_height() != 0:
                    plot.annotate(format(p.get_height().astype(int), 'd'),
                                  ((p.get_x() + p.get_width() / 2).astype(int), p.get_height().astype(int)),
                                  ha='center', va='center',
                                  size=12,
                                  xytext=(0, 8),
                                  textcoords='offset points')
            self.save_fig(self.options.test_names[i], 'absolute models')
            plt.close()

    def save_fig(self, result_name, graph_type):
        plt.savefig(
            self.graph_dir + f'\\{result_name}\\' + f'{graph_type}.svg',
            dpi=600,
            format="svg")
        plt.savefig(
            self.graph_dir + f'\\{graph_type}\\' + f'{result_name}.svg',
            dpi=600,
            format="svg")
