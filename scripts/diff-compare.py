from matplotlib import pyplot as plt
import numpy as np
import scipy
from scipy import stats

cold_diffusions = [0.00099, 0.01189, 0.0000875, 0.00304, 0.0118875]
hot_diffusions = [0.001815, 0.0308775, 0.01419, 0.01607, 0.0108325, 0.0210575, 0.0275375, 0.0233975, 0.03885, 0.0608625]

print(f'cold: {np.mean(cold_diffusions)} +- {np.std(cold_diffusions)}')
print(f'hot: {np.mean(hot_diffusions)} +- {np.std(hot_diffusions)}')

res = stats.ttest_ind(cold_diffusions, hot_diffusions, equal_var=True)
print(res)

with plt.style.context('science'):
    x = np.arange(2)
    y = [np.mean(cold_diffusions), np.mean(hot_diffusions)]
    y_err = [np.std(cold_diffusions), np.std(hot_diffusions)]
    labels = ['Cold', 'Hot']
    fig, ax = plt.subplots()
    ax.bar(x, y, yerr=y_err, align='center', alpha=0.5)
    ax.set_ylabel(r'D ($cm^{2}/s$)')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    plt.tight_layout()
    plt.savefig("diff-compare-fig", dpi=300)
    plt.show()