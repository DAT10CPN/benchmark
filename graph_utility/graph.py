import os
from copy import deepcopy

import pandas as pd


class Graph:
    def __init__(self, options):
        self.options = options
        self.results_dir = os.path.join(os.path.dirname(__file__), '..\\results')
        self.graph_dir = os.path.join(os.path.dirname(__file__), f'..\\graphs\\{self.category}\\')
        self.data_list = deepcopy(options['results'])
        self.name = ""


    def plot(self):
        print(f"Making graph: {self.name}")

    def read_results(self):
        self.data_list = [pd.read_csv(self.results_dir + csv, engine='python') for csv in self.data_list]
