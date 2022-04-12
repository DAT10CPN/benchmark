from graph import Graph


class Lines(Graph):
    def __init__(self, options):
        super().__init__(options)
        self.graph_dir = options.graph_dir + '\\lines\\'
        self.linestyles = [
            [1, 1],
            [2, 2, 10, 2],
            [5, 5],
            [6, 2],
            [3, 1],
            [3, 1, 3, 1, 1, 1],
            [3, 1, 1, 1],
            [3, 5, 1, 5, 1, 5],
            [1, 1, 3, 1, 6, 1],
            [3, 1, 1, 1, 1, 1]]
        self.base_width = 3
        self.other_width = 1.5
        self.base_name = 'base'
        if self.options.enable_graphs == 1:
            self.cutoff_times = [0, 2.5]
            self.keep_percentages = [0.05, 0.25]
        elif self.options.enable_graphs == 2:
            self.cutoff_times = [0, 0.5, 1, 2.5, 5, 10, 20, 30, 60]
            self.keep_percentages = [0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1]
