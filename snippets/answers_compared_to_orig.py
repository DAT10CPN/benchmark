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

for ss in search_strategies:
    print(f" ========= {ss} ==========")
    df_ss = pd.DataFrame(columns=["category", "experiment", "answers"])
    for category in categories:
        df_cat = pd.DataFrame(columns=["category", "experiment", "answers"])
        orig_answers = 0
        for csv in (data_dir / category / ss / "MCC2021-COL").glob("*.csv"):
            df_ex = pd.read_csv(csv)
            answers = len(df_ex.index) - df_ex["answer"].value_counts()["NONE"]
            if csv.stem == "orig":
                orig_answers = answers
            entry = {
                "category": category,
                "experiment": csv.stem,
                "answers": answers,
            }
            df_cat = df_cat.append(entry, ignore_index=True)
            print(entry)
        df_cat["diff"] = df_cat["answers"] - orig_answers
        df_ss = pd.concat([df_ss, df_cat])
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print("Everything:")
        print(df_ss)
        print("Aggregate:")
        print(df_ss.groupby(["experiment"])[["answers", "diff"]].sum())

    for category in categories:
        print(f"{category:<36}", end=" & ")
        for experiment in ["orig", "C", "D", "E", "F", "I", "Q", "U", "IUC", "IUDCEFQ"]:
            print(f'{df_ss[(df_ss["category"] == category) & (df_ss["experiment"] == experiment)].iloc[0]["answers"]:>5} & ', end="")
        print("")
    for category in categories:
        print(f"{category:<36}", end=" & ")
        for experiment in ["orig", "C", "D", "E", "F", "I", "Q", "U", "IUC", "IUDCEFQ"]:
            if experiment == "orig":
                print(
                    f'{int(df_ss[(df_ss["category"] == category) & (df_ss["experiment"] == experiment)].iloc[0]["answers"]):>5} & ',
                    end="")
            else:
                print(f'{int(df_ss[(df_ss["category"] == category) & (df_ss["experiment"] == experiment)].iloc[0]["diff"]):>+5} & ', end="")
        print("")

    df_ss_no_orig = df_ss[df_ss["experiment"] != "orig"]

    sns.set(rc={'figure.figsize': (11, 12)})
    sns.set_theme(style="darkgrid", palette="pastel")
    g = sns.barplot(data=df_ss_no_orig, x="diff", y="experiment", hue="category")
    for container in g.containers:
        g.bar_label(container, fmt="%+g", padding=3)
    g.set_xlabel(f"Answers relative to orig experiment ({ss})")
    g.set_ylabel("Experiment")
    plt.pyplot.tight_layout()

    plt.pyplot.savefig(root / "graphs" / "CPN-4-30-4-2-ioless" / f"{ss}_answers.svg", dpi=600, format="svg")
    plt.pyplot.close()
