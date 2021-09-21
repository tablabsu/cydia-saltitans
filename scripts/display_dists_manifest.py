#! python3
import sys, os, argparse, logging, json, math
from random import random
from matplotlib import pyplot as plt
from scipy import stats as st
import numpy as np

DEFAULT_THRESHOLD = 0.1
MINIMUM_DELAY_FRAMES = 1.0

# --------- UTILITY METHODS --------- 

# Returns distance between points
def dist(x1, y1, x2, y2):
    return math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2))

# -----------------------------------

# Setting up argument parser
parser = argparse.ArgumentParser(description='Display probability distribution of delays between jumps and relative displacement frames from position data referenced in provided manifest file')
parser.add_argument('path', help='Path to manifest file')
parser.add_argument("-t", "--threshold", type=float, help="Threshold of activity, defaults to {0}".format(DEFAULT_THRESHOLD))
parser.add_argument("-mdf", "--min-delay-frames", type=float, help="Coefficient for minimum threshold for number of frames between delays to be plotted, usually 1.0, so minimum delay frames is 1.0 * CLIP_FPS")
parser.add_argument("-g", "--gen-individual", action="store_true", help="Generate individual delay and displacement plots for each dataset, saved in separate folders")
parser.add_argument("-d", "--debug", action="store_true", help="Show debug information")
args = vars(parser.parse_args())

# Setting up logger
format = "%(levelname)s : %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
logging.info("Starting plotting...")
if args.get("debug"):
    logging.getLogger().setLevel(logging.DEBUG)
logging.debug("ARGS: {0}".format(args))

mdf = MINIMUM_DELAY_FRAMES
if args['min_delay_frames']:
    mdf = args['min_delay_frames']

# Read manifest file
if not os.path.exists(args['path']):
    logging.warning("Given path does not exist! Exiting...")
    sys.exit(1)
if not os.path.split(args['path'])[-1].endswith('.json'):
    logging.warning("Given path does not point to a .json file! Exiting...")
    sys.exit(1)
logging.info("Loading manifest file...")
manifest = []
with open(args['path']) as fp:
    manifest = json.load(fp)
datasets = list(set([f['set'] for f in manifest]))
datasets.sort()
logging.debug("Datasets: {0}".format(datasets))

if args.get("gen_individual"):
    if not os.path.exists("saved-delays"):
        os.mkdir("saved-delays")
    if not os.path.exists("saved-disps"):
        os.mkdir("saved-disps")

units = None
total_delays = []
total_disps = []
for set in datasets:
    logging.info("Processing set '{0}'...".format(set))
    set_files = [f for f in manifest if f['set'] == set]
    logging.debug("Set files: {0}".format([os.path.split(p['path'])[-1] for p in set_files]))
    set_delays = []
    set_disps = []
    for f in set_files:
        logging.info("    Processing file '{0}'...".format(os.path.split(f['path'])[-1]))
        if not os.path.exists(f['path']):
            logging.warning("Given path does not exist! Exiting...")
            sys.exit(1)
        if not os.path.split(f['path'])[-1].endswith('.json'):
            logging.warning("Given path does not point to a .json file! Exiting...")
            sys.exit(1)

        objects = []
        canvas = {}
        with open(f['path']) as fp:
            data = json.load(fp)
            objects = data['objects']
            canvas = data['canvas']
        fps = canvas['fps']
        if units is None:
            units = canvas['units']

        # Calculating delays and associated displacements
        logging.info("Calculating delays...")
        threshold = args['threshold']
        if threshold is None:
            threshold = DEFAULT_THRESHOLD
        delays = []
        disps = []
        x = objects[0]['X']
        y = objects[0]['Y']
        d = 1
        for i in range(len(x) - 1):
            disp = dist(x[i], y[i], x[i+1], y[i+1])
            if disp < threshold:
                d += 1
            else:
                if d >= int(mdf * fps):
                    delays.append(d)
                    disps.append(disp)
                    d = 1
        
        # Convert all delays into seconds so clips w/ varying FPS values can be compared
        delays = [int(d / fps) for d in delays]

        set_delays.extend(delays)
        set_disps.extend(disps)
    
    if args.get("gen_individual"):
        setname = set.replace("/", "_")
        
        # Generate and save delay plot
        fig, ax = plt.subplots()
        ax.set_xlabel("t_D (seconds)")
        ax.set_ylabel("Frequency")
        ax.set_xlim(0, 25)
        plt.hist(set_delays, density=True, bins=max(set_delays), color=(0, 0, 0), histtype="step")
        fig.savefig("saved-delays/{0}_delays".format(setname))
        plt.close()

        # Generate and save displacement plot
        fig, ax = plt.subplots()
        ax.set_xlabel("δ ({0})".format(units))
        ax.set_ylabel("Frequency")
        ax.set_xlim(0, 1.0)
        plt.hist(set_disps, density=True, bins=40, color=(0, 0, 0), histtype="step")
        fig.savefig("saved-disps/{0}_disps".format(setname))
        plt.close()

    total_delays.extend(set_delays)
    total_disps.extend(set_disps)

logging.debug("Total Delays: {0}".format(len(total_delays)))
logging.debug("Total Displacements: {0}".format(len(total_disps)))
logging.info("Setting up plots...")

# Delay plot

# Setting up plot
logging.info("Plotting {0} delays...".format(len(total_delays)))
fig, ax = plt.subplots()
ax.set_xlabel("t_D (seconds)")
ax.set_ylabel("Frequency")
ax.set_xlim(0, 25)
d = [i for i in total_delays if i <= 25 and i >= mdf]
hist, bins, _ = plt.hist(d, density=True, bins=max(d), color=(0, 0, 0), histtype='step')

# Fit distribution and plot
params = st.invgamma.fit(d + [0])
logging.info("Delay fit parameters: {0}".format(params))
fit_x = [i/10 for i in list(range(0, 250))]
best_fit = st.invgamma.pdf(fit_x, *params)
plt.plot(fit_x, best_fit, color=(1, 0, 0))

# Show plot
plt.show()

# Save figure
if input("Save figure? ").lower() in ('y', 'yes'):
    logging.info("Saving figure...")
    fig.savefig("figure-delay")
    fig.savefig("figure-delay.svg", format="svg")

# Displacement plot

logging.info("Plotting {0} displacements...".format(len(total_disps)))
fig, ax = plt.subplots()
ax.set_xlabel("δ ({0})".format(units))
ax.set_ylabel("Frequency")
ax.set_xlim(0, 1.0)
d = total_disps
hist, bins, _ = plt.hist(d, density=True, bins=40, color=(0, 0, 0), histtype='step')

# Fit distribution and plot
params = st.expon.fit(d)
logging.info("Displacement fit parameters: {0}".format(params))
fit_x = [i/100 for i in list(range(math.ceil(min(d) * 100), 100))]
best_fit = st.expon.pdf(fit_x, *params)
plt.plot(fit_x, best_fit, color=(1, 0, 0))

# Show plot
plt.show()

# Save figure
if input("Save figure? ").lower() in ('y', 'yes'):
    logging.info("Saving figure...")
    fig.savefig("figure-displacement")
    fig.savefig("figure-displacement.svg", format="svg")
    