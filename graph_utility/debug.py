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
        data = pd.concat(csvs, axis=1)
        data.sort_index(level=0, inplace=True)

        relevant_rows = [
            'orig@verification time',
            'pagg-parT-parP@verification time',
        ]
        data = data.drop(data[data['orig@answer'] == 'NONE'].index)
        data = data.drop(data[data['pagg-parT-parP@answer'] == 'NONE'].index)
        data = data[data['orig@verification time'] > data['pagg-parT-parP@verification time']*5]
        data = data.drop(data[(data['pagg-parT-parP@rule 0'] == 0) & (data['pagg-parT-parP@rule 1'] == 0) & (data['pagg-parT-parP@rule 2'] == 0)].index)
        #df = df[(df.one > 0) | (df.two > 0) | (df.three > 0) & (df.four < 1)]
        data = data[relevant_rows]

        self.everything = data

    def plot(self):
        self.everything.to_csv(self.options.graph_dir + f"\\{self.name}.csv")
