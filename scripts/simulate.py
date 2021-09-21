#! python3
import sys, os, argparse, logging, json, math, random
from scipy import stats as st
import numpy as np

# ----------------- CONSTANTS -----------------

DEFAULT_WIDTH = 27.94
DEFAULT_HEIGHT = 21.59
DEFAULT_UNITS = "cm"
DEFAULT_FPS = 1

DELAY_SHAPE = 1.7239
DELAY_LOC = -0.0667
DELAY_SCALE = 3.5195
DISP_LOC = 0.1
DISP_SCALE = 0.2556

MAX_DELAY = 25
MAX_DISP = 1.0

# --------- UTILITY METHODS / CLASSES --------- 

# Parse time string into number of seconds
def parse_time_string(tstr):
    pass

# Sample from delay distribution
def sampleDelay():
    d = st.invgamma.rvs(DELAY_SHAPE, loc=DELAY_LOC, scale=DELAY_SCALE)
    while d > MAX_DELAY:
        d = st.invgamma.rvs(DELAY_SHAPE, loc=DELAY_LOC, scale=DELAY_SCALE)
    return d

# Sample from displacement distribution
def sampleDisp():
    d = st.expon.rvs(loc=DISP_LOC, scale=DISP_SCALE)
    while d > MAX_DISP:
        d = st.expon.rvs(loc=DISP_LOC, scale=DISP_SCALE)
    return d

# Sample from angle distribution
def sampleAngle():
    return random.uniform(-math.pi, math.pi)

class Bean:
    def __init__(self, x, y):
        self.pos = [x, y]
        self.delay = sampleDelay()
        self.angle = sampleAngle()
    def move(self):
        if (self.delay > 0):
            self.delay -= (1 / DEFAULT_FPS)
        if (self.delay <= 0):
            self.delay = sampleDelay()
            self.angle = sampleAngle()
            disp = sampleDisp()

# ---------------------------------------------

# Setting up argument parser
parser = argparse.ArgumentParser(description='Simulate motion of beans over period of time, output position data file')
parser.add_argument("-n", "--num-beans", type=int, required=True, help="Number of beans in simulation")
parser.add_argument("-l", "--length", required=True, help="Time string representing length of simulation (i.e., '2h30m')")
parser.add_argument("-d", "--debug", action="store_true", help="Show debug information")
args = vars(parser.parse_args())

# Setting up logger
format = "%(levelname)s : %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
logging.info("Starting plotting...")
if args.get("debug"):
    logging.getLogger().setLevel(logging.DEBUG)
logging.debug("ARGS: {0}".format(args))

# Setting up canvas for pos data file
canvas = {
    "width": DEFAULT_WIDTH,
    "height": DEFAULT_HEIGHT,
    "units": DEFAULT_UNITS,
    "fps": DEFAULT_FPS
}

# Creating beans
beans = []
for i in range(args.get("num_beans")):
    beans.append(Bean(0, 0))

for i, b in enumerate(beans):
    print("{0} {1} {2}".format(i, b.pos[0], b.pos[1]))
