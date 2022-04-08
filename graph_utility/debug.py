import pandas as pd

from graph_utility.graph import Graph


# Class for testing
class DebugGraph(Graph):

    def __init__(self, options):
        super().__init__(options)
        self.everything = pd.DataFrame()
        self.name = 'debug'

    def prepare_data(self):
        csvs = self.options.read_results
        for i, csv in enumerate(csvs):
            csv.set_index(["model name", "query index"], inplace=True)
            csv.rename(columns={col: f"{self.options.test_names[i]}@{col}" for col in csv.columns}, inplace=True)
        everything = pd.concat(csvs, axis=1)
        everything.sort_index(level=0, inplace=True)

        everything = everything.drop(everything[everything['orig@answer'] != 'NONE'].index)
        everything = everything.drop(everything[everything['relv-pagg-parT-parP@answer'] == 'NONE'].index)

        self.everything = everything[['orig@verification time', 'relv-pagg-parT-parP@verification time']]


    def plot(self):
        self.everything.to_csv(self.options.graph_dir + f"\\{self.name}.csv")
