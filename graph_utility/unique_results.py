import copy
import os


def find_unique_results(options):
    os.makedirs(options.graph_dir + f'\\unique-results\\')
    options.graph_dir = options.graph_dir + f'\\unique-results\\'

    csvs = copy.deepcopy(options.read_results)
    for i, csv in enumerate(csvs):
        csv.set_index(["model name", "query index"], inplace=True)

    # Individual comparisons
    for index1, experiment1 in enumerate(csvs):
        for index2, experiment2 in enumerate(csvs):
            if index1 == index2:
                continue

            experiment1_answers = compare_two_experiments(experiment1, experiment2)
            experiment1_answers.to_csv(
                f"{options.graph_dir}/({experiment1.iloc[0]['test name']})_answers_that_({experiment2.iloc[0]['test name']})_did_not_find.csv")

    # Compare across all
    unique_answers_across_all(options)


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


def unique_answers_across_all(options):
    print("todo")
