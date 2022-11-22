import random, argparse, logging
from enum import Enum
from matplotlib import pyplot as plt, transforms
from matplotlib import rcParams as rcp
from matplotlib import ticker
import numpy as np

# ----------------- CONSTANTS -----------------

JUMP_SIZE = 1
SHADE_POS = 0
END_POS = 200
START_MIN = 1
START_MAX = 50

# --------- UTILITY METHODS / CLASSES --------- 

class Motion(Enum):
    DIFFUSE = 1
    BALLISTIC = 2

class Bean:
    def __init__(self):
        self.pos = 0
        self.motion = 0
    def findShade(self):
        time = 0
        if self.motion == Motion.BALLISTIC:
            dir = round(random.uniform(0, 1)) * 2 - 1
            while self.pos > SHADE_POS and self.pos < END_POS:
                self.pos += dir * JUMP_SIZE
                time += 1
            if self.pos >= END_POS:
                return 10000000
            return time
        elif self.motion == Motion.DIFFUSE:
            while self.pos > SHADE_POS and self.pos < END_POS:
                dir = round(random.uniform(0, 1)) * 2 - 1
                self.pos += dir * JUMP_SIZE
                time += 1
            if self.pos >= END_POS:
                return 10000000
            return time

# ---------------------------------------------

# Setting up argument parser
parser = argparse.ArgumentParser(description='Simulate shade-finding success of beans in 1 dimension, displays probability distributions of time to find shade')
parser.add_argument("num_beans", type=int, help="Number of beans in simulation")
parser.add_argument("-t", "--title", action='store_true', help="Show titles on plots")
parser.add_argument("-d", "--debug", action="store_true", help="Show debug information")
args = vars(parser.parse_args())

# Setting up logger
format = "%(levelname)s : %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
if args.get("debug"):
    logging.getLogger().setLevel(logging.DEBUG)
logging.info("Starting simulation...")

b = Bean()
logging.info("Calculating diffuse shade times...")
diffuse_times = []
b.motion = Motion.DIFFUSE
for i in range(args.get("num_beans")):
    b.pos = round(random.uniform(START_MIN, START_MAX))
    diffuse_times.append(b.findShade())
diffuse_times = [1.0 / t for t in diffuse_times]

logging.info("Calculating ballistic shade times...")
ballistic_times = []
b.motion = Motion.BALLISTIC
for i in range(args.get("num_beans")):
    b.pos = round(random.uniform(START_MIN, START_MAX))
    ballistic_times.append(b.findShade())
ballistic_times = [1.0 / t for t in ballistic_times]

logging.info("Displaying plots...")

# Disabling individual plots while working on combined

'''
logging.info("Displaying diffuse probability distribution...")
fig, ax = plt.subplots()
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel(f'Rate (N = {args.get("num_beans")})')
ax.set_ylabel("Frequency")
if args.get("title"):
    ax.set_title("Rate of finding shade (diffuse)")
plt.hist(diffuse_times, bins=np.logspace(np.log10(0.00001), np.log10(10)), density=True, color=(0, 0, 0), histtype='step')
#plt.xlim([0, 0.05])
plt.show()
if input("Save figure? ").lower() in ('y', 'yes'):
    logging.info("Saving figure...")
    fig.savefig("figure-shade-diffuse")
'''

'''
logging.info("Displaying ballistic probability distribution...")
fig, ax = plt.subplots()
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel(f'Rate (N = {args.get("num_beans")})')
ax.set_ylabel("Frequency")
if args.get("title"):
    ax.set_title("Rate of finding shade (ballistic)")
plt.hist(ballistic_times, bins=np.logspace(np.log10(0.00001), np.log10(10)), density=True, color=(0, 0, 0), histtype='step')
#plt.xlim([0, 0.05])
plt.show()
if input("Save figure? ").lower() in ('y', 'yes'):
    logging.info("Saving figure...")
    fig.savefig("figure-shade-ballistic")
'''

#rcp.update({'font.size': 16})
logging.info("Displaying combined plot...")
with plt.style.context(['science']):
    fig = plt.figure(figsize=(3.5, 2.625 * 1.2))
    subfigs = fig.subfigures(2, 1, hspace=0.0, height_ratios=[1, 1])
    axs = subfigs[1].subplots(1, 2, sharey=True, gridspec_kw={"width_ratios" : [1, 3]})
    subfigs[1].subplots_adjust(wspace=1)
    topAx = subfigs[0].add_subplot(111)
    topAx.get_xaxis().set_ticks([])
    topAx.get_xaxis().set_ticklabels([])
    topAx.get_yaxis().set_ticks([])
    topAx.get_yaxis().set_ticklabels([])
    topAx.imshow(plt.imread('bean-shade-sim.png'))
    topAx.text(-0.15, 0.95, "a", transform=topAx.transAxes)
    # Axis broken figure
    axs[0].set_xscale('log')
    axs[0].set_yscale('log')
    axs[1].set_xscale('log')
    axs[1].set_yscale('log')
    axs[0].set_xlabel('RFS (1/s)')
    axs[0].set_ylabel("P(RFS)")
    # Hide spines where axis breaks
    axs[0].spines['right'].set_visible(False)
    axs[1].spines['left'].set_visible(False)
    # Set ticks to appear on opposite sides
    axs[0].yaxis.tick_left()
    axs[1].yaxis.tick_right()
    # Draw diagonal axis break lines
    dw = .015
    dh = .015
    kwargs = dict(transform=axs[0].transAxes, color='k', clip_on=False, linewidth=0.75)
    axs[0].plot((1 - dw, 1 + dw), (1 - dh, 1 + dh), **kwargs)  # top-left diagonal
    axs[0].plot((1 - dw, 1 + dw), (-dh, +dh), **kwargs)  # bottom-left diagonal
    kwargs.update(transform=axs[1].transAxes)
    dw /= 3
    axs[1].plot((-dw, +dw), (1 - dh, 1 + dh), **kwargs)  # top-right diagonal
    axs[1].plot((-dw, +dw), (-dh, +dh), **kwargs)        # bottom-right diagonal
    # Set x limits
    axs[0].set_xticks([0.0000001199], labels=['0'])
    axs[1].set_xticks([1e-4, 1e-2, 1])
    axs[0].set_xlim(0.00000008, 0.000000199)
    axs[1].set_xlim(0.000007, 10)
    axs[0].get_xaxis().set_tick_params(which='minor', size=0)
    axs[0].get_xaxis().set_tick_params(which='minor', width=0) 
    axs[0].text(-0.7, 0.95, "b", transform=axs[0].transAxes)
    axs[0].hist(diffuse_times, label="Diffuse", bins=np.logspace(np.log10(0.0000001), np.log10(10)), density=True, color=(1, 0, 0), histtype='step', linewidth=3)
    axs[0].hist(ballistic_times, label="Ballistic", bins=np.logspace(np.log10(0.0000001), np.log10(10)), density=True, color=(0, 0, 1), histtype='step')
    axs[1].hist(diffuse_times, label="Diffuse", bins=np.logspace(np.log10(0.0000001), np.log10(10)), density=True, color=(1, 0, 0), histtype='step', linewidth=3)
    axs[1].hist(ballistic_times, label="Ballistic", bins=np.logspace(np.log10(0.0000001), np.log10(10)), density=True, color=(0, 0, 1), histtype='step')
    plt.tight_layout()
    logging.info("Saving figure...")
    fig.savefig("fig5", dpi=300)
    fig.savefig("fig5.svg")
