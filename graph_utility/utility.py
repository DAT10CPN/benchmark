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
        df['error'] = df.apply(
            lambda row: 1 if row['prev place count'] == 0 else 500, axis=1)
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
