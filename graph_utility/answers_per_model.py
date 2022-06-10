import os
from dataclasses import dataclass

import pandas as pd
import numpy as np
from graph import Graph

pd.options.mode.chained_assignment = None


@dataclass()
class Answers():
    graph_name: str
    transformed_data: pd.DataFrame()


class AnswersByModel(Graph):

    def __init__(self, options):
        super().__init__(options)
        self.graph_dir = options.graph_dir + '\\answers'
        self.name = 'answers by model'

    def prepare_data(self):
        if not os.path.exists(self.graph_dir):
            os.makedirs(self.graph_dir)
        total_answers = pd.DataFrame()

        for data in self.data_list:
            current_test_name = data.iloc[0]['test name']
            if current_test_name != self.options.base_name:
                continue

            remove_non_answers = data[data['answer'] != 'NONE']
            if self.options.petri_net_type == "CPN":
                remove_non_answers['model name'] = remove_non_answers['model name'].str.split(r'-COL').str.get(0)
            else:
                remove_non_answers['model name'] = remove_non_answers['model name'].str.split(r'-PT').str.get(0)
            total_answers[self.options.base_name] = remove_non_answers.groupby(['model name'])['model name'].count()

        for data in self.data_list:
            current_test_name = data.iloc[0]['test name']
            if current_test_name == self.options.base_name:
                continue

            remove_non_answers = data[data['answer'] != 'NONE']
            if self.options.petri_net_type == "CPN":
                remove_non_answers['model name'] = remove_non_answers['model name'].str.split(r'-COL').str.get(0)
            else:
                remove_non_answers['model name'] = remove_non_answers['model name'].str.split(r'-PT').str.get(0)
            df = remove_non_answers.groupby(['model name'])['model name'].count()
            total_answers[current_test_name] = df - total_answers[self.options.base_name]

        #if self.options.petri_net_type == 'PT':
        #    total_answers = total_answers[(np.abs(total_answers['newC']) > 0) | (np.abs(total_answers['withS']) > 0)]
        #    total_answers.sort_values(by=['newC', 'withS'], inplace=True, ascending=False)
        total_answers.to_csv(self.graph_dir + "\\answers_by_model.csv")
        total_answers.to_csv(self.graph_dir + "\\answers_by_model-latex.csv", sep='&', line_terminator="\\\\ \\hline\n")

    def plot(self):
        pass
