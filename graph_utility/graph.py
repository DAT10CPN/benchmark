import copy


class Graph:
    def __init__(self, options):
        self.options = copy.deepcopy(options)
        self.data_list = copy.deepcopy(options.read_results)
        self.name = ""
        self.custom_sort_dict = {'orig': 0, 'C': 1, 'D': 2, 'E': 3, 'F': 4, 'I': 5, 'S': 6, 'T': 7, 'Q': 8, 'ISC': 9,
                                 'ITC': 10, 'ISDCEFQ': 11, 'ITDCEFQ': 12}

    def plot(self):
        print(f"Making graph: {self.name}")
