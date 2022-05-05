import os
from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from graph import Graph

pd.options.mode.chained_assignment = None


@dataclass()
class Answers():
    graph_name: str
    transformed_data: pd.DataFrame()


class AnswerSimplificationBars(Graph):

    def __init__(self, options):
        super().__init__(options)
        self.graph_dir = options.graph_dir + '\\answers'
        self.name = 'answers'
        self.answers = []

    def prepare_data(self):
        # data from each csv will become a row in the combined dataframe, such that row index is the test name,
        # and columns are 'not answered', 'simplified', and 'reduced'.
        combined = pd.DataFrame()
        simple_combined = pd.DataFrame()
        for index, data in enumerate(self.data_list):
            num_test_cases = len(data)
            errors = data['error'].value_counts()

            data.drop(data[data['error'] <= 3].index, inplace=True)

            # Change 'NONE' value to 'not answered', and 'TRUE' and 'FALSE' to 'answered'
            data['answer'] = data['answer'].replace(['TRUE', 'FALSE'], 'answered')
            data['answer'] = data['answer'].replace(['NONE'], 'not answered')

            # Same thing for simplification, renames to simplified and not simplified, based on bool value
            data['solved by query simplification'] = data['solved by query simplification'].replace(True, 'simplified')
            data['solved by query simplification'] = data['solved by query simplification'].replace(False,
                                                                                                    'not simplified')

            # Get counts of 'answered' and 'not answered'
            answers = (data['answer'].value_counts()).to_frame()

            # Get counts of 'simplified' and 'not simplified'
            simplifications = (data['solved by query simplification'].value_counts()).to_frame()

            # Combine into same dataframe, with column being the test name, and row indices being above metrics
            answers.rename(columns={'answer': self.options.test_names[index]}, inplace=True)
            simplifications.rename(columns={'solved by query simplification': self.options.test_names[index]},
                                   inplace=True)

            temp = answers.append(simplifications)

            # Might not have these columns, due to faulty test, so wrap in try-except
            try:
                num_answered = temp.T['answered']
            except KeyError:
                num_answered = 0

            try:
                num_simplified = temp.T['simplified']
            except KeyError:
                num_simplified = 0

            # Create new column 'reduced'
            reduced = int(num_answered - num_simplified)
            temp.loc['reduced'] = reduced
            for error_code in range(1, 4):
                try:
                    if errors[error_code] > 0:
                        temp.loc[error_code] = errors[error_code]

                except KeyError:
                    temp.loc[error_code] = 0
                    continue
            temp = temp.T
            # As per default we want to remove these two columns that Nicolaj does not like
            # But as we saw, we can have faulty experiments-30-60-1-1 where some of these wont exist
            # And if we try to remove something that does not exist, everything stops working
            columns_to_remove = ['answered', 'not simplified']
            for col in columns_to_remove:
                try:
                    temp.drop(columns=col, inplace=True)
                except KeyError:
                    continue

            if 'reduced' not in temp.columns:
                temp['reduced'] = 0
            if 'simplified' not in temp.columns:
                temp['simplified'] = 0
            if 'not answered' not in temp.columns:
                temp['not answered'] = 0

            temp.rename(columns={'reduced': 'Answered'}, inplace=True)
            temp.rename(columns={'simplified': 'Answered (simplification)'}, inplace=True)
            temp.rename(columns={'not answered': 'Timeout in verification (4)'}, inplace=True)
            temp.rename(columns={3: 'Error in reduction (3)'}, inplace=True)
            temp.rename(columns={2: 'Timeout in unfolding (2)'}, inplace=True)
            temp.rename(columns={1: 'Error in col reduction (1)'}, inplace=True)

            # Reorder the columns so that bars are stacked nicely
            temp = temp[[
                'Answered',
                'Answered (simplification)',
                'Timeout in verification (4)',
                'Error in reduction (3)',
                'Timeout in unfolding (2)',
                'Error in col reduction (1)'
            ]]

            # Add data from this experiment, to results from other results
            combined = combined.append(temp)

            simple_graph_data = {'answers': num_answered, 'not answered': num_test_cases - num_answered}
            simple_temp = pd.DataFrame(data=simple_graph_data, index=[self.options.test_names[index]])
            simple_combined = simple_combined.append(simple_temp)
        self.transformed_data = [
            Answers(
                graph_name='answers_splits',
                transformed_data=combined
            ),
            Answers(
                graph_name='answers_simple',
                transformed_data=simple_combined
            )
        ]

    def plot(self):
        os.makedirs(self.graph_dir)
        # Plot the plot
        sns.set_theme(style="darkgrid", palette="pastel")
        for answers in self.transformed_data:
            plot = answers.transformed_data.plot(kind='barh', width=0.75, linewidth=2, figsize=(10, 10), stacked=True)

            plt.legend(bbox_to_anchor=(0.35, 1.12), loc='upper left', borderaxespad=0)
            plt.xlabel("test instances")
            plot.set_ylabel(self.options.folder)
            plt.tight_layout()

            # Find max width, in order to move the very small numbers away from the bars
            max_width = 0
            for p in plot.patches:
                left, bottom, width, height = p.get_bbox().bounds
                max_width = max(width, max_width)
            # Plot the numbers in the bars
            for p in plot.patches:
                left, bottom, width, height = p.get_bbox().bounds
                plot.annotate(int(width), xy=(left + width / 2, bottom + height / 2),
                              ha='center', va='center', rotation=45)

            plt.savefig(self.graph_dir + f'\\{answers.graph_name}.svg', dpi=600, format="svg")
            plt.close()
