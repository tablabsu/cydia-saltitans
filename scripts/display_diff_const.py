#! python
from matplotlib import pyplot as plt
import numpy as np
from matplotlib import rcParams as rcp

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

theta = np.polyfit(size, msd, 1)
fit_line = np.poly1d(theta)

rcp.update({
    'font.size': 18,
    'axes.labelsize': 14
})
fig, ax = plt.subplots()
plt.xlabel('Bean size (mm)')
plt.ylabel('Slope of mean-squared displacement')
plt.scatter(size, msd, color='black')
plt.plot(size, fit_line(size), linewidth=2, color=(1, 0, 0))
plt.tight_layout()
plt.show()
fig.savefig("figure-msd-size")