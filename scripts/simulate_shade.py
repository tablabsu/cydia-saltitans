import random, argparse, logging
from enum import Enum
from matplotlib import pyplot as plt
from matplotlib import rcParams as rcp

# ----------------- CONSTANTS -----------------

JUMP_SIZE = 1
SHADE_POS = 0
END_POS = 200
START_MIN = 20
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
                return 100000
            return time
        elif self.motion == Motion.DIFFUSE:
            while self.pos > SHADE_POS and self.pos < END_POS:
                dir = round(random.uniform(0, 1)) * 2 - 1
                self.pos += dir * JUMP_SIZE
                time += 1
            if self.pos >= END_POS:
                return 100000
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

logging.info("Displaying diffuse probability distribution...")
fig, ax = plt.subplots()
#ax.set_xscale('log')
#ax.set_yscale('log')
ax.set_xlabel(f'Rate (N = {args.get("num_beans")})')
ax.set_ylabel("Frequency")
if args.get("title"):
    ax.set_title("Rate of finding shade (diffuse)")
plt.hist(diffuse_times, bins=30, density=True, color=(0, 0, 0), histtype='step')
plt.xlim([0, 0.05])
plt.show()
if input("Save figure? ").lower() in ('y', 'yes'):
    logging.info("Saving figure...")
    fig.savefig("figure-shade-diffuse")

logging.info("Displaying ballistic probability distribution...")
fig, ax = plt.subplots()
#ax.set_xscale('log')
#ax.set_yscale('log')
ax.set_xlabel(f'Rate (N = {args.get("num_beans")})')
ax.set_ylabel("Frequency")
if args.get("title"):
    ax.set_title("Rate of finding shade (ballistic)")
plt.hist(ballistic_times, bins=30, density=True, color=(0, 0, 0), histtype='step')
plt.xlim([0, 0.05])
plt.show()
if input("Save figure? ").lower() in ('y', 'yes'):
    logging.info("Saving figure...")
    fig.savefig("figure-shade-ballistic")