from pathlib import Path

import pandas as pd
import matplotlib as plt
import seaborn as sns

root = Path(__file__).parent.parent
data_dir = root / "results" / "CPN-4-30-4-2-ioless"
categories = [
    "ReachabilityCardinality",
    "ReachabilityFireability",
    "LTLCardinality",
    "LTLFireability",
    "CTlCardinality",
    "CTLFireability",
]
search_strategies = [
#    "BestFS",
    "DFS",
#    "RDFS"
]
rule_name_to_id_map = {
    "I": "0",
    "S": "1",
    "T": "1",
    "U": "1",
    "D": "2",
    "C": "3",
    "E": "4",
    "F": "5",
    "Q": "6",
}

for ss in search_strategies:
    print(f" ========= {ss} ==========")
    df_ss = pd.DataFrame(columns=["category", "experiment", "C", "D", "E", "F", "I", "Q", "U"])
    for category in categories:
        df_cat = pd.DataFrame(columns=["category", "experiment", "C", "D", "E", "F", "I", "Q", "U"])
        for csv in (data_dir / category / ss / "MCC2021-COL").glob("*.csv"):
            df_ex = pd.read_csv(csv)
            entry = {
                "category": category,
                "experiment": csv.stem,
            }
            for rule in ["C", "D", "E", "F", "I", "Q", "U"]:
                entry[rule] = df_ex[f'rule {rule_name_to_id_map[rule]}'].sum()
                entry[rule + "%"] = (df_ex[f'rule {rule_name_to_id_map[rule]}'] > 0).sum() / float(len(df_ex.index))
            df_cat = df_cat.append(entry, ignore_index=True)
            print(entry)
        df_ss = pd.concat([df_ss, df_cat])
    print(df_ss)

    # Absolute applications
    for category in categories:
        for experiment in ["C", "D", "E", "F", "I", "Q", "U", "IUC", "IUDCEFQ"]:
            for rule in experiment:
                applications = df_ss[(df_ss["category"] == category) & (df_ss["experiment"] == experiment)].iloc[0][rule]
                if len(experiment) > 1:
                    print(f"\multicolumn{{1}}{{c|}}{{{applications:>8}}} & ", end="")
                else:
                    print(f"{applications:>8} & ", end="")
        print("")

    print("\n")

    # Percentage of queries with at least one applications
    for category in categories:
        for experiment in ["C", "D", "E", "F", "I", "Q", "U", "IUC", "IUDCEFQ"]:
            for rule in experiment:
                applications = 100 * df_ss[(df_ss["category"] == category) & (df_ss["experiment"] == experiment)].iloc[0][rule + "%"]
                if len(experiment) > 1:
                    print(f"\multicolumn{{1}}{{c|}}{{{applications:>6.1f}\\%}} & ", end="")
                else:
                    print(f"{applications:>6.1f}\\% & ", end="")
        print("")