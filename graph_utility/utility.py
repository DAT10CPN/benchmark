import copy
from dataclasses import dataclass

import numpy as np


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


def color(t):
    a = np.array([0.5, 0.5, 0.5])
    b = np.array([0.5, 0.5, 0.5])
    c = np.array([1.0, 1.0, 1.0])
    d = np.array([0.0, 0.33, 0.67])

    return a + (b * np.cos(2 * np.pi * (c * t + d)))


def get_total_time(row):
    return row['colored reduce time'] + row['unfold time'] + row['reduce time'] + row['verification time']


def get_unfolded_size(row):
    return row['unfolded place count'] + row['unfolded transition count']


def get_colored_reduced_size(row):
    return row['colored reduce place count'] + row['colored reduce transition count']


def get_reduced_size(row):
    return row['reduced place count'] + row['reduced transition count']


def sanitise_df_list(result_list, test_names):
    for index, df in enumerate(result_list):
        df['test name'] = test_names[index]
    sanitised_list = []
    for index, df in enumerate(result_list):
        print(f"{(index + 1) / len(result_list) * 100:.2f}%")
        sanitised_list.append(sanitise_df(df))
    return sanitised_list


def sanitise_df(df):
    df = infer_errors(df)
    df = infer_simplification_from_prev_size_0_rows(df)

    return df


def write_results_with_errors(options):
    results_to_write = copy.deepcopy(options.read_results)
    for index, result in enumerate(results_to_write):
        result.to_csv(f"{options.graph_dir}\\errors\\{options.test_names[index]}.csv")


def is_previous_error(row):
    return row['error'] < 69420


def phase_1_errors(df):
    df['error'] = df.apply(
        lambda row: 1 if row['original place count'] == 0 or (
                row['colored reduce time'] == 0.0 and not ('orig' in row['test name'])) else 69420, axis=1)
    return df


def phase_2_errors(df):
    def infer_phase_2_errors(row):
        if row['error'] < 69420:
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
        if row['error'] < 69420:
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
        if row['error'] < 69420:
            return row['error']
        elif row['verification time'] == 0.0 and row['answer'] == 'NONE' and row[
            'solved by query simplification'] is False:
            return 4
        return row['error']

    df['error'] = df.apply(
        lambda row: min(row['error'], infer_phase_4_errors(row)),
        axis=1)
    return df


def infer_errors(df):
    df = phase_1_errors(df)
    df = phase_2_errors(df)
    df = phase_3_errors(df)
    df = phase_4_errors(df)
    return df


# This can happen if query simplification is used
def infer_simplification_from_prev_size_0_rows(df):
    df['answer'] = df.apply(
        lambda row: 'TRUE' if (get_reduced_size(row) == 0.0 and get_unfolded_size(row) > 0 and row['error'] == 0) else
        row['answer'], axis=1)
    df['solved by query simplification'] = df.apply(
        lambda row: True if (get_reduced_size(row) == 0.0 and get_unfolded_size(row) > 0 and row['error'] == 0) else
        row[
            'solved by query simplification'], axis=1)
    return df
