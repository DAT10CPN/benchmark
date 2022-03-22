import os
import shutil

import numpy as np
import pandas as pd

def compare_two_tests(exp_1, exp_1_name, data_list, test_names, consistency_dir, category):
    matrix_dict = dict()

    for test_index, data in enumerate(data_list):
        if test_names[test_index] == exp_1_name:
            matrix_dict[test_names[test_index]] = np.nan
            continue
        elif test_index < test_names.index(exp_1_name):
            matrix_dict[test_names[test_index]] = np.nan
            continue

        combined = exp_1.merge(data, left_index=True, right_index=True)
        combined = combined.loc[~(combined[f"{test_names[test_index]}@answer"] == combined[f"{exp_1_name}@answer"])]
        num_consistent_rows = int(len(combined))
        matrix_dict[test_names[test_index]] = num_consistent_rows
        if num_consistent_rows > 0:
            combined.to_csv(
                f'{consistency_dir}/inconsistent_rows_({exp_1_name})_({test_names[test_index]})_{category}.csv')

    return matrix_dict


def check_consistency(options):
    data_list = [pd.read_csv(options['chosen dir'] + csv) for csv in options['chosen results']]
    for i, data in enumerate(data_list):
        data.drop(data.index[data['answer'] == 'NONE'], inplace=True)
        data.set_index(["model name", "query index"], inplace=True)
        data.rename(columns={col: f"{options['test names'][i]}@{col}" for col in data.columns}, inplace=True)

    matrix_df = pd.DataFrame()
    for index, exp_1 in enumerate(data_list):
        row = compare_two_tests(exp_1, options['test names'][index], data_list, options['test names'], options['graph dir'], options['category'])
        matrix_df = matrix_df.append(row, ignore_index=True)

    new_rows_indices = dict()
    for index, name in enumerate(options['test names']):
        new_rows_indices[index] = name
    matrix_df = matrix_df.rename(index=new_rows_indices)
    matrix_df.to_csv(options['graph dir'])
    print("Done")
