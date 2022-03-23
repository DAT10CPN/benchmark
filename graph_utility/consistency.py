import numpy as np
import pandas as pd


def compare_two_results(exp_1, exp_1_index, data_list, options):
    consistency_row = dict()
    exp_1_name = options.test_names[exp_1_index]

    for exp_2_index, exp_2 in enumerate(data_list):
        exp_2_result_name = options.test_names[exp_2_index]

        # Dont compare to itself
        if exp_2_result_name == exp_1_name:
            consistency_row[exp_2_result_name] = np.nan
            continue
        # Make sure that we do not compare x and y, and later y and x
        elif exp_2_index < exp_1_index:
            consistency_row[exp_2_result_name] = np.nan
            continue

        combined = exp_1.merge(exp_2, left_index=True, right_index=True)
        combined = combined.loc[~(combined[f"{exp_2_result_name}@answer"] == combined[f"{exp_1_name}@answer"])]
        num_consistent_rows = int(len(combined))
        consistency_row[exp_2_result_name] = num_consistent_rows
        # If any inconsistencies, write the inconsistent rows between two single results to file
        if num_consistent_rows > 0:
            combined.to_csv(
                f'{options.graph_dir}/inconsistent_rows_({exp_1_name})_({exp_2_result_name})_{options.category}.csv')

    return consistency_row


def check_consistency(options):
    # We are now mutating the data in options, so check consistency should always be last
    for i, data in enumerate(options.read_results):
        data.drop(data.index[data['answer'] == 'NONE'], inplace=True)
        data.set_index(["model name", "query index"], inplace=True)
        data.rename(columns={col: f"{options.test_names[i]}@{col}" for col in data.columns}, inplace=True)

    consistency_matrix = pd.DataFrame()
    for index, exp_1 in enumerate(options.read_results):
        row = compare_two_results(exp_1, index, options.read_results, options)
        consistency_matrix = consistency_matrix.append(row, ignore_index=True)

    new_rows_indices = dict()
    for index, name in enumerate(options.test_names):
        new_rows_indices[index] = name
    consistency_matrix = consistency_matrix.rename(index=new_rows_indices)
    consistency_matrix.to_csv(f"{options.graph_dir}/matrix.csv")
    print("Done")
