#! python3
import sys, os, argparse, logging, json, math
import numpy as np
from random import random
from matplotlib import pyplot as plt

# --------- UTILITY METHODS --------- 

# Returns distance between points
def dist(x1, y1, x2, y2):
    return math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2))

# -----------------------------------

DEFAULT_FPS = 1

# Setting up argument parser
parser = argparse.ArgumentParser(description="Display mean-squared displacement (MSD) plots from position data files")
parser.add_argument("path", nargs='+', help="Path to file containing position data")
parser.add_argument("-d", "--debug", action="store_true", help="Show debug information")
parser.add_argument("-f", "--fps", type=int, help="FPS of input data")
args = vars(parser.parse_args())

# Setting up logger
format = "%(levelname)s : %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
logging.info("Starting plotting...")
if args.get("debug"):
    logging.getLogger().setLevel(logging.DEBUG)
logging.debug("ARGS: {0}".format(args))

fps = DEFAULT_FPS
if args['fps']:
    fps = args['fps']

# Calculate MSD data for each object in each file
objects_msd = []
for path in args['path']:
    # Check that file at path exists and ends in .json
    if not os.path.exists(path):
        logging.warning("Given path does not exist! Exiting...")
        sys.exit(1)
    if not os.path.split(path)[-1].endswith(".json"):
        logging.warning("Given path does not point to a .json file! Exiting...")
        sys.exit(1)

    objects = []
    canvas = {}
    # Read position data from file
    logging.info("Reading position data from '{0}'...".format(os.path.split(path)[-1]))
    with open(path) as fp:
        data = json.load(fp)
        objects = data['objects']
        canvas = data['canvas']

    logging.info("Calculating squared displacements from '{0}'".format(os.path.split(path)[-1]))

    # Calculate squared displacements
    for i, obj in enumerate(objects):
        if len(objects_msd) < (i + 1):
            # 'New' object
            o = { 'tau': [], 'msd': [] }
            tau = range(fps, int(len(obj['X']) / 2), fps)
            for t in tau:
                # Pull out X and Y coordinate lists
                tau_x = obj['X']
                tau_y = obj['Y']

                # Calculate distance between points apart by interval tau, then square displacement
                tau_dist = [dist(tau_x[i], tau_y[i], tau_x[i+t], tau_y[i+t]) for i in range(len(tau_x) - t)]
                tau_dist = [math.pow(i, 2) for i in tau_dist]

                # Average the displacement of those intervals
                #msd = sum(tau_dist) / len(tau_dist)
                msd = tau_dist

                # Add to object's tau and msd list
                o['tau'].append(int(t / fps))
                o['msd'].append(msd)
            objects_msd.append(o)
        else:
            # Object seen in previous file
            o = objects_msd[i]
            tau = range(fps, int(len(obj['X']) / 2), fps)
            for t in tau:
                # Pull out X and Y coordinate lists
                tau_x = obj['X']
                tau_y = obj['Y']

                # Calculate distance between points apart by interval tau, then square displacement
                tau_dist = [dist(tau_x[i], tau_y[i], tau_x[i+t], tau_y[i+t]) for i in range(len(tau_x) - t)]
                tau_dist = [math.pow(i, 2) for i in tau_dist]

                # Average the displacement of those intervals
                #msd = sum(tau_dist) / len(tau_dist)
                msd = tau_dist

                # Add to object's tau and msd list
                o['tau'].append(int(t / fps))
                o['msd'].append(msd)
            objects_msd[i] = o
        

# Merge tau entries for each object
logging.info("Merging squared displacements into MSD...")
for obj in objects_msd:
    tau = []
    msd = []
    for t in range(1, max(obj['tau'])):
        sd = []
        for i, u in enumerate(obj['tau']):
            if t == u:
               sd.extend(obj['msd'][i]) 
        if len(sd) > 0:
            msd_val = sum(sd) / len(sd)
            tau.append(t)
            msd.append(msd_val)
    obj['tau'] = tau
    obj['msd'] = msd

# Set up plots
logging.info("Setting up plots...")
fig, ax = plt.subplots()
for i, obj in enumerate(objects_msd):
    # Calculate natural log of tau and msd
    tau = [math.log(i, 10) if i != 0 else i for i in obj['tau']]
    msd = [math.log(i, 10) if i != 0 else i for i in obj['msd']]

    color = (random(), random(), random())

    # Plot scatter of log tau/msd
    plt.scatter(tau, msd, color=color)

    # Plot trendlines of log tau/msd
    pf = np.polyfit(tau, msd, 1)
    p = np.poly1d(pf)
    plt.plot(tau, p(tau), '--', label="Object {1} slope: {0:.2f}".format(pf[0], i), color=color)

plt.title("Log MSD over Log Tau")
plt.xlabel("Log Tau")
plt.ylabel("Log MSD ({0})".format(canvas['units'] + "^2"))
#if len(objects_msd) > 1:
#    plt.legend()
plt.legend()
plt.show()

if input("Save figure? ").lower() in ('y', 'yes'):
    logging.info("Saving figure...")
    plt.tight_layout()
    fig.savefig("figure-msd", dpi=144)
