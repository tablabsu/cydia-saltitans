#! python
from matplotlib import pyplot as plt
import numpy as np
from matplotlib import rcParams as rcp
from scipy import stats

DATA_PATH = '../misc/msd-size-plot/msd-slopes-unlogged.txt'

print(f'Reading MSD slopes and bean sizes from {DATA_PATH}...')
dataset = []
msd = []
size = []
with open(DATA_PATH) as fp:
    data = fp.readlines()
    for l in data:
        line = l.split(":")
        dataset.append(line[0])
        msd.append(float(line[1]))
        size.append(float(line[2]))
print(f'Read {len(dataset)} datasets.')
print(f'Read {len(msd)} MSD slopes.')
print(f'Read {len(size)} bean sizes.')

msd = [x / 4 for x in msd]

print(msd)

res = stats.linregress(size, msd)
fit_line = np.poly1d([res.slope, res.intercept])

print(f'Linear regression p value: {res.pvalue}')

#rcp.update({ 'font.size': 18, 'axes.labelsize': 14 })
with plt.style.context(['science']):
    fig, ax = plt.subplots()
    plt.xlabel('L (mm)')
    plt.ylabel(r'D ($cm^{2}/s$)')
    with plt.style.context(['scatter']):
        plt.scatter(size, msd, color='black')
    plt.plot(size, fit_line(size), linewidth=2, color=(1, 0, 0))
    plt.tight_layout()
    plt.show()
    fig.savefig("fig2-diff-const", dpi=300)