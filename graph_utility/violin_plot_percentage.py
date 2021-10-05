import matplotlib.pyplot as plt
import seaborn as sns

def plot(data_list, test_names, rules):
    sns.set_style("whitegrid")

    for index, data in enumerate(data_list):
        data = data.drop(data[(data['solved by query simplification']) | (data.answer == 'NONE')].index)
        grouped_data = data.groupby(['model name'])[rules].agg('sum')

        percentages = ((grouped_data > 0) * 1)
        plot = sns.violinplot(data=percentages)
        plot.set(title=f'({test_names[index]}) chance for a rule to be used in a model', ylabel='Chance to be used')
        for p in plot.patches:
            plot.annotate(format(p.get_height(), '.1f'),
                          (p.get_x() + p.get_width() / 2., p.get_height()),
                          ha='center', va='center',
                          size=10,
                          xytext=(0, 8),
                          textcoords='offset points')
        plt.savefig(f'../graphs/{test_names[index]}_rule_violin_percentage.png')
        plt.clf()