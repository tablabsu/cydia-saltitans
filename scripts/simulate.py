#! python3
import sys, os, argparse, logging, json, random
import math as m
import numpy as np
from scipy import stats as st

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
    total_secs = 0
    numstr = "0"
    for c in tstr:
        if c.isdigit():
            numstr += c
        else:
            num = int(numstr)
            if c == "s":
                total_secs += num
            if c == "m":
                total_secs += num * 60
            if c == "h":
                total_secs += num * 3600
            numstr = "0"
    return total_secs

# Sample from delay distribution
def sampleDelay():
    d = st.invgamma.rvs(DELAY_SHAPE, loc=DELAY_LOC, scale=DELAY_SCALE, random_state=1)
    while d > MAX_DELAY:
        d = st.invgamma.rvs(DELAY_SHAPE, loc=DELAY_LOC, scale=DELAY_SCALE, random_state=1)
    return d

# Sample from displacement distribution
def sampleDisp():
    d = st.expon.rvs(loc=DISP_LOC, scale=DISP_SCALE, random_state=1)
    while d > MAX_DISP:
        d = st.expon.rvs(loc=DISP_LOC, scale=DISP_SCALE, random_state=1)
    return d

# Sample from angle distribution
def sampleAngle():
    return random.uniform(-m.pi, m.pi)

class Bean:
    def __init__(self, x, y):
        self.pos = np.array([float(x), float(y)])
        self.delay = sampleDelay()
    def move(self):
        if (self.delay > 0):
            self.delay -= (1 / DEFAULT_FPS)
        if (self.delay <= 0):
            # Sample delay/disp/angle
            self.delay = sampleDelay()
            angle = sampleAngle()
            disp = sampleDisp()
            # Create velocity vector and rotation matrix
            vel = np.array([0, disp])
            rot = np.array([[m.cos(angle), -m.sin(angle)], [m.sin(angle), m.cos(angle)]])
            # Rotate velocity vector and apply to position vector
            rot_vel = np.dot(rot, vel)
            self.pos += rot_vel


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

objects = []
for i in range(len(beans)):
    objects.append({"X": [], "Y": []})

for t in range(parse_time_string(args.get("length"))):
    print("Frame {0}: ".format(t))
    for i, b in enumerate(beans):
        b.move()
        objects[i]["X"].append(b.pos[0])
        objects[i]["Y"].append(b.pos[1])
        print("    Bean {0} - X: {1} Y: {2} Delay: {3} ".format(i, round(b.pos[0], 2), round(b.pos[1], 2), round(b.delay, 2)))

pos_files = list(filter(lambda n : n.endswith(".json"), os.listdir("../experiments/simulations/")))
pos_files = list(map(lambda n : int(n.split(".")[0].split("_")[-1]), pos_files))

pos_filename = "../experiments/simulations/pos_data_{0}.json".format(max(pos_files) + 1 if len(pos_files) > 0 else 0)

with open(pos_filename, "w+") as fp:
    json.dump({"canvas": canvas, "objects": objects}, fp)