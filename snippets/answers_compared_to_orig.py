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
    "BestFS",
    "DFS",
    "RDFS"
]

for ss in search_strategies:
    df_ss = pd.DataFrame(columns=["category", "experiment", "answers"])
    for category in categories:
        df_cat = pd.DataFrame(columns=["category", "experiment", "answers"])
        orig_answers = 0
        for csv in (data_dir / category / ss / "MCC2021-COL").glob("*.csv"):
            df_ex = pd.read_csv(csv)
            answers = len(df_ex.index) - df_ex["answer"].value_counts()["NONE"]
            if csv.stem == "orig":
                orig_answers = answers
            else:
                df_cat = df_cat.append({
                    "category": category,
                    "experiment": csv.stem,
                    "answers": answers,
                }, ignore_index=True)
        df_cat["answers"] = df_cat["answers"] - orig_answers
        df_ss = pd.concat([df_ss, df_cat])
    print(df_ss)

    sns.set(rc={'figure.figsize': (11, 12)})
    sns.set_theme(style="darkgrid", palette="pastel")
    g = sns.barplot(data=df_ss, x="answers", y="experiment", hue="category")
    g.set_xlabel(f"Answers relative to orig experiment ({ss})")
    g.set_ylabel("Experiment")

    plt.pyplot.savefig(root / "graphs" / "CPN-4-30-4-2-ioless" / f"{ss}_answers.svg", dpi=600, format="svg")
    plt.pyplot.close()
