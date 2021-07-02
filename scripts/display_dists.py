#! python3
import sys, os, argparse, logging, json, math
from random import random
from matplotlib import pyplot as plt

DEFAULT_THRESHOLD = 0.1

# --------- UTILITY METHODS --------- 

# Returns distance between points
def dist(x1, y1, x2, y2):
    return math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2))

# -----------------------------------

# Setting up argument parser
parser = argparse.ArgumentParser(description="Display probability distribution of delays between jumps and relative displacement between frames from json position data files")
parser.add_argument("path", nargs='+', help="Path to file containing position data")
parser.add_argument("-t", "--threshold", type=float, help="Threshold of activity, defaults to {0}".format(DEFAULT_THRESHOLD))
parser.add_argument("-o", "--objects", help="Index of objects to calculate delays for, accepts comma-separated list of indices")
parser.add_argument("-b", "--bin-factor", type=float, help="Bins are set to show every value in input data, this accepts a multiplier to increase or reduce that number (defaults to 1)")
parser.add_argument("-d", "--debug", action="store_true", help="Show debug information")
args = vars(parser.parse_args())

# Setting up logger
format = "%(levelname)s : %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
logging.info("Starting plotting...")
if args.get("debug"):
    logging.getLogger().setLevel(logging.DEBUG)
logging.debug("ARGS: {0}".format(args))

total_delays = []
total_disps = []
# Iterate through each given path
for p_num, path in enumerate(args['path']):

    # Check that file at path exists and ends in .json
    if not os.path.exists(path):
        logging.warning("Given path does not exist! Exiting...")
        sys.exit(1)
    if not os.path.split(path)[-1].endswith(".json"):
        logging.warning("Given path does not point to a .json file! Exiting...")
        sys.exit(1)

    # Loading position data from file
    logging.info("Loading position data...")
    objects = []
    canvas = {}
    with open(path) as fp:
        data = json.load(fp)
        objects = data['objects']
        canvas = data['canvas']

    # Filtering out specified objects
    obj_i = []
    if args['objects']:
        obj_i = [int(i) for i in args['objects'].split(",")]
    else:
        obj_i = range(len(objects))

    # Calculating delays and associated displacements
    logging.info("Calculating delays...")
    threshold = args['threshold']
    if threshold is None:
        threshold = DEFAULT_THRESHOLD
    obj_delays = []
    obj_disps = []
    for o in obj_i:
        x = objects[o]['X']
        y = objects[o]['Y']
        d = 1
        delays = []
        disps = []
        for i in range(len(x) - 1):
            disp = dist(x[i], y[i], x[i+1], y[i+1])
            if disp < threshold:
                d += 1
            else:
                delays.append(d)
                disps.append(disp)
                d = 1
        obj_delays.append(delays)
        obj_disps.append(disps)

    # Combine delays and displacements into total delays and displacements
    for i, o in enumerate(obj_delays):
        if p_num == 0:
            total_delays.append(o)
        else:
            total_delays[i].extend(o)
    for i, o in enumerate(obj_disps):
        if p_num == 0:
            total_disps.append(o)
        else:
            total_disps[i].extend(o)

logging.debug("Total Delays: {0}".format(len(total_delays[0])))
logging.debug("Total Displacements: {0}".format(len(total_disps[0])))
logging.info("Setting up plots...")

# Setting up delay plot
if input("View delay plot? ").lower() in ('y', 'yes'):
    fig, ax = plt.subplots()
    fig.suptitle("Delay Distribution Histogram")
    ax.set_title("Motion threshold: {0} {1}".format(threshold, canvas['units']))
    ax.set_xlabel("Delay (frames)")
    ax.set_ylabel("Log of Frequency")
    ax.set_xlim(0, 25)
    bin_factor = 1
    if args['bin_factor']:
        bin_factor = args['bin_factor']
    for i, d in enumerate(obj_delays):
        bins = 1
        if len(d) > 0:
            bins = int(max(d) * bin_factor)
        plt.hist(d, bins=bins, color=(random(), random(), random()), label="Object {0}".format(i))
    if len(obj_delays) > 1:
        plt.legend()
    plt.yscale('log')
    plt.show()

    # Saving figure
    if input("Save figure? ").lower() in ('y', 'yes'):
        logging.info("Saving figure...")
        fig.savefig("figure-delay")

# Setting up displacement plot
if input("View displacement plot? ").lower() in ('y', 'yes'):
    fig, ax = plt.subplots()
    #fig.suptitle("Displacement Distribution Histogram")
    ax.set_title("Displacement Distribution Histogram")
    ax.set_xlabel("Displacement ({0})".format(canvas['units']))
    ax.set_ylabel("Frequency")
    ax.set_xlim(0, 1.0)
    bin_factor = 1
    if args['bin_factor']:
        bin_factor = args['bin_factor']
    for i, d in enumerate(obj_disps):
        plt.hist(d, bins=40, color=(random(), random(), random()), label="Object {0}".format(i))
    if len(obj_disps) > 1:
        plt.legend()
    plt.show()

    # Saving figure
    if input("Save figure? ").lower() in ('y', 'yes'):
        logging.info("Saving figure...")
        fig.savefig("figure-displacement")

# Setting up delay vs. displacement plot
if input("View delay vs. displacement plot? ").lower() in ('y', 'yes'):
    fig, ax = plt.subplots()
    ax.set_title("Delay vs. Displacement")
    ax.set_xlabel("Delay (frames)")
    ax.set_ylabel("Displacement ({0})".format(canvas['units']))
    ax.set_xlim(0, 200)
    ax.set_ylim(0, 1.0)
    for i in range(len(obj_disps)):
        plt.scatter(obj_delays[i], obj_disps[i], color=(random(), random(), random()))
    if len(obj_disps) > 1:
        plt.legend()
    plt.show()

    # Saving figure
    if input("Save figure? ").lower() in ('y', 'yes'):
        logging.info("Saving figure...")
        fig.savefig("figure-delay-displacement")





