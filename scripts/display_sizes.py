#! python
from re import S
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

with plt.style.context('science'):
    fig, axs = plt.subplots(2, 1, figsize=(3.5, 2.625 * 1.5), gridspec_kw={"height_ratios" : [2, 1]})
    axs = axs.flatten()
    axs[0].get_xaxis().set_ticks([])
    axs[0].get_xaxis().set_ticklabels([])
    axs[0].get_yaxis().set_ticks([])
    axs[0].get_yaxis().set_ticklabels([])
    axs[0].imshow(plt.imread('fig1-photo.png'))
    axs[1].hist(sizes, edgecolor="black", fill=False, linewidth=1, density=True)
    axs[1].set_xlabel("L (mm)")
    axs[1].set_ylabel("P(L)")
    axs[0].text(-0.15, 0.95, "a", transform=axs[0].transAxes)
    axs[1].text(-0.1, 0.95, "b", transform=axs[1].transAxes)
    plt.tight_layout()
    fig.savefig("fig1", dpi=300)
