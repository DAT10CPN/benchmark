import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from graph import Graph

pd.options.mode.chained_assignment = None


class AnswerSimplificationBars(Graph):

    def __init__(self, options):
        super().__init__(options)
        self.transformed_data = pd.DataFrame()
        self.graph_dir = options.graph_dir
        self.name = 'answers'

    def prepare_data(self):
        # data from each csv will become a row in the combined dataframe, such that row index is the test name,
        # and columns are 'not answered', 'simplified', and 'reduced'.
        combined = pd.DataFrame()
        for index, data in enumerate(self.data_list):
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
            # Reorder the columns so that bars are stacked nicely
            temp = temp[["reduced", "simplified", "not answered", 1, 2, 3]]
            temp.rename(columns={1: '1 error in color reducer'}, inplace=True)
            temp.rename(columns={2: '2 error in unfolding'}, inplace=True)
            temp.rename(columns={3: '3 error in reducer'}, inplace=True)
            temp.rename(columns={4: '4 error in verification'}, inplace=True)

            # Add data from this experiment, to results from other results
            combined = combined.append(temp)
        self.transformed_data = combined

    def plot(self):
        # Plot the plot
        sns.set_theme(style="darkgrid", palette="pastel")
        plot = self.transformed_data.plot(kind='barh', width=0.75, linewidth=2, figsize=(10, 10), stacked=True)

        plt.legend(bbox_to_anchor=(0.35, 1.12), loc='upper left', borderaxespad=0)
        plt.xlabel("test instances")
        plt.ylabel('experiments-30-60-1-1')

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
        plt.savefig(self.graph_dir + '\\answers.svg', dpi=600, format="svg")
        plt.close()
