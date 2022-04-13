import copy
import os

import numpy as np
import pandas as pd


def find_unique_results(options):
    os.makedirs(options.graph_dir + f'\\unique-results\\')
    graph_dir = options.graph_dir + f'\\unique-results\\'

    csvs = copy.deepcopy(options.read_results)
    for i, csv in enumerate(csvs):
        csv.set_index(["model name", "query index"], inplace=True)

    print("Starting to compare individual results")
    # Individual comparisons
    unique_answers_matrix = pd.DataFrame()
    for index1, experiment1 in enumerate(csvs):
        unique_answers_row = dict()
        for index2, experiment2 in enumerate(csvs):

            if index1 == index2:
                unique_answers_row[experiment2.iloc[0]['test name']] = np.nan
                continue

            experiment1_answers = compare_two_experiments(experiment1, experiment2)
            # Add cell value for the comparison between the two experiments
            unique_answers_row[experiment2.iloc[0]['test name']] = len(experiment1_answers)

            experiment1_answers.loc[f"{experiment2.iloc[0]['test name']} answers"] = ["-----" for col in
                                                                                      experiment1_answers.columns]

            experiment2_answers = compare_two_experiments(experiment2, experiment1)
            combined = experiment1_answers.append(experiment2_answers)

            # experiment1_answers.to_csv(
            # f"{graph_dir}/({experiment1.iloc[0]['test name']})_answers_that_({experiment2.iloc[0]['test name']})_did_not_find.csv")

            if index1 < index2:
                combined.to_csv(
                    f"{graph_dir}/({experiment1.iloc[0]['test name']})-({experiment2.iloc[0]['test name']}).csv")

        print(f"{(index1 + 1) / len(csvs) * 100:.2f}%")

        # Append row to matrix
        unique_answers_matrix = unique_answers_matrix.append(unique_answers_row, ignore_index=True)

    # Write matrix
    new_rows_indices = dict()
    for index, name in enumerate(options.test_names):
        new_rows_indices[index] = name
    unique_answers_matrix = unique_answers_matrix.rename(index=new_rows_indices)
    unique_answers_matrix.to_csv(f"{graph_dir}/unique_answers_matrix.csv")


# Find the results that experiment1 got, that experiment2 did not
def compare_two_experiments(experiment1, experiment2):
    experiment1_answers = experiment1.drop(experiment1[experiment1[f'answer'] == 'NONE'].index)
    experiment2_non_answered = experiment2.drop(experiment2[experiment2['answer'] != 'NONE'].index)

    experiment1_answers.rename(
        columns={col: f"{experiment1_answers.iloc[0]['test name']}@{col}" for col in experiment1_answers.columns},
        inplace=True)
    experiment2_non_answered.rename(columns={col: f"{experiment2_non_answered.iloc[0]['test name']}@{col}" for col in
                                             experiment2_non_answered.columns}, inplace=True)

    experiment1_answers_that_experiment2_did_not_get = experiment1_answers.merge(experiment2_non_answered,
                                                                                 left_index=True, right_index=True)

    return experiment1_answers_that_experiment2_did_not_get
