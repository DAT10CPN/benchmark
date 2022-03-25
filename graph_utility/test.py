import pandas as pd

from graph_utility.graph import Graph


# Class for testing
class TestGraph(Graph):

    def __init__(self, options):
        super().__init__(options)
        self.everything = pd.DataFrame()
        self.name = 'test'

    def prepare_data(self):
        def orig_is_smaller(row):
            return (row['orig@colored reduce place count'] + row['orig@colored reduce transition count']) < (
                        row['parT@colored reduce place count'] + row['parT@colored reduce transition count'])

        csvs = self.options.read_results
        for i, csv in enumerate(csvs):
            csv.set_index(["model name", "query index"], inplace=True)
            csv.rename(columns={col: f"{self.options.test_names[i]}@{col}" for col in csv.columns}, inplace=True)
        everything = pd.concat(csvs, axis=1)
        everything.sort_index(level=0, inplace=True)

        relevant_rows = []
        for test_name in self.options.test_names:
            relevant_rows.append(f"{test_name}@colored reduce place count")
            relevant_rows.append(f"{test_name}@colored reduce transition count")
        everything = everything[relevant_rows]
        everything['inequal'] = everything.apply(
            lambda row: 1 if orig_is_smaller(row) else 0,
            axis=1)
        self.everything = everything

    def plot(self):
        self.everything.to_csv(self.options.graph_dir + f"{self.name}.csv")
