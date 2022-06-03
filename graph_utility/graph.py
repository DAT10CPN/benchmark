import copy


class Graph:
    def __init__(self, options):
        self.options = copy.deepcopy(options)
        self.data_list = copy.deepcopy(options.read_results)
        self.name = ""
        self.custom_sort_dict = {'base': 0, 'orig': 0, 'C': 1, 'D': 2, 'E': 3, 'F': 4, 'I': 5, 'S': 6, 'T': 7, 'U': 8, 'Q': 9,
                                 'ISC': 10, 'IUC': 11,
                                 'ITC': 12, 'ISDCEFQ': 13, 'ITDCEFQ': 14, 'IUDCEFQ': 15}

    def plot(self):
        pass
