import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import utility
from lines import Lines
import os

class VerificationTimeRatio(Lines):
    def __init__(self, options):
        super().__init__(options)
        self.graph_dir = options.graph_dir + '\\ratios\\'
        self.name = 'verification_time_ratio'
        self.plot_ready = pd.DataFrame()

    def prepare_data(self):
        if not self.options.base_name in self.options.test_names:
            return
        combined = utility.combined_pd(self.data_list, self.options.test_names)
        for data in self.data_list:
            current_test_name = data.iloc[0]['test name']
            if current_test_name == self.options.base_name:
                continue
            base_time = self.options.base_name + '@verification time'
            current_time = current_test_name + '@verification time'
            base_answer = self.options.base_name + '@answer'
            current_answer = current_test_name + '@verification time'
            temp = np.where(combined[base_answer] != 'NONE',
                                                          np.where(combined[current_answer] != 'NONE',
                                                                   np.where(
                                                                       combined[base_time] == combined[current_time], 1,
                                                                       combined[base_time] / combined[current_time]),
                                                                   np.nan), np.nan)
            temp.sort()
            self.plot_ready[current_test_name] = temp

    def plot(self):
        os.makedirs(self.graph_dir)
        plot = self.create_lineplot(self.plot_ready)
        plot.set(
            ylabel='ratio',
            xlabel='queries')
        try:
            plot.set(yscale="log")
        except:
            plot.set(yscale="linear")
        plt.title(f'{self.options.base_name} verification time / other tests')

        plt.savefig(
            self.graph_dir + f'{self.name}.svg',
            bbox_inches='tight', dpi=600, format="svg")
        plt.close()
