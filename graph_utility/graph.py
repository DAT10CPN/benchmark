import copy


class Graph:
    def __init__(self, options):
        self.options = copy.deepcopy(options)
        self.data_list = copy.deepcopy(options.read_results)
        self.name = ""

    def plot(self):
        print(f"Making graph: {self.name}")
