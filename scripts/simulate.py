#! python3
import sys, os, argparse, logging, json, random, time
import math as m
import numpy as np
from scipy import stats as st

# ----------------- CONSTANTS / GLOBALS -----------------

DEFAULT_WIDTH = 27.94
DEFAULT_HEIGHT = 21.59
DEFAULT_UNITS = "cm"
DEFAULT_FPS = 1

DELAY_SHAPE = 1.7535932839923403
DELAY_LOC = -0.07100098076125703
DELAY_SCALE = 3.5906318280526532
DISP_LOC = 0.10000000000000009
DISP_SCALE = 0.2587618978181744

DISP_MATRIX_DIMS = (1000, 1000)
DELAY_MATRIX_DIMS = (1000, 1000)

MAX_DELAY = 25
MAX_DISP = 1.0

SAMPLE_UNIFORM = False

delay_mat = np.array([])
disp_mat = np.array([])

wt_max = 0
ang_bins = []
bin_size = 0

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
    i = np.random.randint(DELAY_MATRIX_DIMS[0], size=2)
    d = delay_mat[i[0]][i[1]]
    while d > MAX_DELAY:
        i = np.random.randint(DELAY_MATRIX_DIMS[0], size=2)
        d = delay_mat[i[0]][i[1]]
    return d - 1

# Sample from displacement distribution
def sampleDisp():
    i = np.random.randint(DISP_MATRIX_DIMS[0], size=2)
    d = disp_mat[i[0]][i[1]]
    while d > MAX_DISP:
        i = np.random.randint(DISP_MATRIX_DIMS[0], size=2)
        d = disp_mat[i[0]][i[1]]
    return d

# Sample from angle distribution
def sampleAngle():
    if SAMPLE_UNIFORM:
        return random.uniform(-m.pi, m.pi)
    else:
        b = random.choices(ang_bins, weights=ad_vals)[0]
        return random.uniform(b['min'], b['max'])

class Bean:
    def __init__(self, x, y):
        self.pos = np.array([float(x), float(y)])
        self.delay = sampleDelay()
        self.disp = sampleDisp()
        self.angle = sampleAngle()
    def move(self):
        if (self.delay > 0):
            self.delay -= (1 / DEFAULT_FPS)
        if (self.delay <= 0):
            # Sample delay/disp/angle
            self.delay = sampleDelay()
            self.angle += sampleAngle()
            # Create velocity vector and rotation matrix
            vel = np.array([0, self.disp])
            rot = np.array([[m.cos(self.angle), -m.sin(self.angle)], [m.sin(self.angle), m.cos(self.angle)]])
            # Rotate velocity vector and apply to position vector
            rot_vel = np.dot(rot, vel)
            self.pos += rot_vel
            # Sample disp for next jump
            self.disp = sampleDisp()


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
logging.info("Starting simulation...")
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

# Creating delay/disp sample matrix
delay_mat = st.invgamma.rvs(DELAY_SHAPE, loc=DELAY_LOC, scale=DELAY_SCALE, size=DELAY_MATRIX_DIMS)
disp_mat = st.expon.rvs(loc=DISP_LOC, scale=DISP_SCALE, size=DISP_MATRIX_DIMS)

# Creating angular disp bins
ad_vals = [0.26903049527169126,0.2073026569684351,0.1892987041299854,0.17849633242691562,0.15894918363088453,0.14300282540254328,0.15483399441066753,0.13631564291969053,0.14506042001265182,0.1275708658267294,0.12448447391156658,0.12808526447925625,0.12036928469134951,0.16254997419857453,0.16923715668142691,0.1856979135622956,0.12191248064893091,0.12962846043683765,0.12294127795398518,0.1306572577418922,0.11934048738629498,0.11779729142871409,0.1306572577418919,0.13117165639441905,0.12757086582672966,0.15740598767330288,0.17592433916427969,0.21861942732403267,0.24022417073017135,0.25051214378071407]
ad_bins = [0.0,0.20943951023931953,0.41887902047863906,0.6283185307179586,0.8377580409572781,1.0471975511965976,1.2566370614359172,1.4660765716752366,1.6755160819145563,1.8849555921538759,2.0943951023931953,2.3038346126325147,2.5132741228718345,2.722713633111154,2.9321531433504733,3.141592653589793,3.3510321638291125,3.560471674068432,3.7699111843077517,3.979350694547071,4.1887902047863905,4.39822971502571,4.607669225265029,4.817108735504349,5.026548245743669,5.235987755982988,5.445427266222308,5.654866776461628,5.864306286700947,6.073745796940266,6.283185307179586]
bin_size = np.mean([ad_bins[i + 1] - ad_bins[i] for i in range(0, len(ad_bins) - 1)])
for i, v in enumerate(ad_vals):
    ang_bins.append({"val": v, "min": ad_bins[i], "max": ad_bins[i+1]})
wt_max = sum(ad_vals)

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
        print("    Bean {0} - X: {1} Y: {2} Delay: {3} Disp: {4}".format(i, round(b.pos[0], 2), round(b.pos[1], 2), round(b.delay, 2), round(b.disp, 2)))

pos_files = list(filter(lambda n : n.endswith(".json"), os.listdir("../experiments/simulations/")))
pos_files = list(map(lambda n : int(n.split(".")[0].split("_")[-1]), pos_files))

pos_filename = "../experiments/simulations/pos_data_{0}.json".format(max(pos_files) + 1 if len(pos_files) > 0 else 0)

with open(pos_filename, "w+") as fp:
    json.dump({"canvas": canvas, "objects": objects}, fp)