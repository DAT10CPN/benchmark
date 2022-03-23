class Graph:
    def __init__(self, options):
        self.options = options
        self.data_list = options.read_results
        self.name = ""

    def plot(self):
        print(f"Making graph: {self.name}")
