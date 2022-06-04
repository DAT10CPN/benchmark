import copy
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass()
class Options:
    """Class for keeping track of options chosen from the gui"""
    result_dir: str
    graph_dir: str
    results_to_plot: list
    category: str
    folder: str
    test_names: [str]
    chosen_graphs: [str]
    read_results: []
    do_consistency_check: bool
    enable_graphs: int
    debug: bool
    unique_results: bool
    petri_net_type: str
    all_options: bool
    search_strategy: str
    base_name: str
    overwrite: bool
    folder_name: str
    model_folder: str
    chosen_directory: str


def add_total_time(data, petri_net_type, remove_nones):
    if remove_nones:
        data_to_extract_total_time_from = data[data['answer'] != 'NONE']
    else:
        data_to_extract_total_time_from = data
    res_df = copy.deepcopy(data_to_extract_total_time_from)
    if petri_net_type == 'CPN':
        res_df['total time'] = data_to_extract_total_time_from.apply(
            cpn_get_total_time,
            axis=1)
    elif petri_net_type == 'PT':
        res_df['total time'] = data_to_extract_total_time_from.apply(
            pt_get_total_time,
            axis=1)
    return res_df


def combined_pd(read_results, test_names):
    copy_results = copy.deepcopy(read_results)
    for i, csv in enumerate(copy_results):
        csv.set_index(["model name", "query index"], inplace=True)
        csv.rename(columns={col: f"{test_names[i]}@{col}" for col in csv.columns}, inplace=True)
    everything = pd.concat(copy_results, axis=1)
    everything.sort_index(level=0, inplace=True)
    return everything


def color(t):
    a = np.array([0.5, 0.5, 0.5])
    b = np.array([0.5, 0.5, 0.5])
    c = np.array([1.0, 1.0, 1.0])
    d = np.array([0.0, 0.33, 0.67])

    return a + (b * np.cos(2 * np.pi * (c * t + d)))


def cpn_get_total_time(row):
    return row['colored reduce time'] + row['unfold time'] + row['reduce time'] + row['verification time']


def pt_get_total_time(row):
    return row['reduce time'] + row['verification time']


def get_unfolded_size(row):
    return row['unfolded place count'] + row['unfolded transition count']


def get_colored_reduced_size(row):
    return row['colored reduce place count'] + row['colored reduce transition count']


def get_reduced_size(row):
    return row['reduced place count'] + row['reduced transition count']


def sanitise_df_list(options):
    result_list = [pd.read_csv(options.result_dir + "\\" + csv) for csv in
                   options.results_to_plot]

    for index, df in enumerate(result_list):
        df['test name'] = options.test_names[index]
    sanitised_list = []
    for index, df in enumerate(result_list):
        if not options.all_options:
            print(f"{(index + 1) / len(result_list) * 100:.2f}%")
        if options.petri_net_type == 'CPN':
            sanitised_list.append(cpn_infer_errors(df))
        elif options.petri_net_type == 'PT':
            sanitised_list.append(pt_infer_errors(df))

    return sanitised_list


def write_results_with_errors(options):
    results_to_write = copy.deepcopy(options.read_results)
    for index, result in enumerate(results_to_write):
        result.to_csv(f"{options.graph_dir}\\errors\\{options.test_names[index]}.csv")


def is_previous_error(row):
    return row['error'] < 500


def phase_1_errors(df, petri_net_type):
    if petri_net_type == 'CPN':
        df['error'] = df.apply(
            lambda row: 1 if row['original place count'] == 0 else 500, axis=1)
    elif petri_net_type == 'PT':
        df['error'] = 500
        # df['error'] = df.apply(
        #     lambda row: 1 if row['prev place count'] == 0 else 500, axis=1)
    return df


def phase_2_errors(df):
    def infer_phase_2_errors(row):
        if row['error'] < 500:
            return row['error']
        elif row['unfold time'] == 0.0:
            return 2
        return row['error']

    df['error'] = df.apply(
        lambda row: min(row['error'], infer_phase_2_errors(row)),
        axis=1)
    return df


def phase_3_errors(df):
    def infer_phase_3_errors(row):
        if row['error'] < 500:
            return row['error']
        elif row['reduce time'] == 0.0:
            return 3
        return row['error']

    df['error'] = df.apply(
        lambda row: min(row['error'], infer_phase_3_errors(row)),
        axis=1)
    return df


def phase_4_errors(df):
    def infer_phase_4_errors(row):
        if row['error'] < 500:
            return row['error']
        elif row['verification time'] == 0.0 and row['answer'] == 'NONE' and row[
            'solved by query simplification'] is False:
            return 4
        return row['error']

    df['error'] = df.apply(
        lambda row: min(row['error'], infer_phase_4_errors(row)),
        axis=1)
    return df


def cpn_infer_errors(df):
    df = phase_1_errors(df, petri_net_type='CPN')
    df = phase_2_errors(df)
    df = phase_3_errors(df)
    df = phase_4_errors(df)
    return df


def pt_infer_errors(df):
    phase_1_errors(df, petri_net_type='PT')
    df = phase_3_errors(df)
    df = phase_4_errors(df)
    return df


def get_col_names(columns):
    col_names = [col for col in columns]
    if not ('orig' in col_names):
        return col_names

    index_of_orig = col_names.index('orig')
    if index_of_orig != 0:
        col_at_index_0 = col_names[0]
        col_names[0] = 'orig'
        col_names[index_of_orig] = col_at_index_0

    return col_names


def sanity_check_is_rule_used(options):
    rule_to_index_mapping = {
        'I': 0,
        'T': 1,
        'S': 1,
        'U': 1,
        'D': 2,
        'C': 3,
        'E': 4,
        'F': 5,
        'Q': 6
    }

    for result in options.read_results:
        test_name = result.iloc[0]['test name']
        if test_name == options.base_name:
            continue

        rule_indices = [rule_to_index_mapping[rule] for rule in list(test_name) if rule.isupper()]
        for rule in rule_indices:
            num_applications = result[f"rule {rule}"].sum()
            if num_applications == 0:
                print(f"\033[91mCHECK '{test_name}' RESULTS IN {options.chosen_directory}\033[0m")
                with open(options.graph_dir + "/meta.txt", mode='a') as file:
                    file.write(f"{test_name} rule {rule} was used: {num_applications} times. Check results\n")
