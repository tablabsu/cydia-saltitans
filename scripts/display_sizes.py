#! python
import numpy as np
import statistics as st
from random import random
from matplotlib import pyplot as plt
from matplotlib import rcParams as rcp

BEAN_SIZE_PATH = '../misc/beansizes.txt'

print(f'Reading bean sizes from {BEAN_SIZE_PATH}')
sizes = []
with open(BEAN_SIZE_PATH) as fp:
    data = fp.readlines()
    sizes = [float(d) for d in data]

#color = ((random() * 0.5) + 0.5, (random() * 0.5) + 0.5, (random() * 0.5) + 0.5)
color = (0.56078, 0.66274, 0.6)

print(f'Processed {len(sizes)} bean size measurements.')
print(f'Mean: {st.mean(sizes)}')
print(f'Stdev: {st.stdev(sizes)}')
print(f'Min: {min(sizes)}')
print(f'Max: {max(sizes)}')

rcp.update({'font.size': 30})
fig, ax = plt.subplots()
plt.hist(
    sizes, 
    edgecolor="black", 
    #color=color,
    #histtype='step',
    fill=False,
    linewidth=2,
    density=True
)
plt.xlabel("Diameter (mm)")
plt.ylabel("P(diameter)")
plt.tight_layout()
plt.show()
fig.savefig("figure-sizes")
