#! python3
import sys, os, argparse, logging, json, math
import numpy as np
from matplotlib import pyplot as plt

# --------- UTILITY METHODS --------- 

# Returns distance between points
def dist(x1, y1, x2, y2):
    return math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2))

# -----------------------------------


# Setting up argument parser
parser = argparse.ArgumentParser(description="Display activity from position data file")
parser.add_argument("path", help="Path to file containing position data")
parser.add_argument("-i", "--interval", type=int, help="Interval between frame activity calculation, defaults to 1")
parser.add_argument("-d", "--debug", action="store_true", help="Show debug information")
args = vars(parser.parse_args())

# Setting up logger
format = "%(levelname)s : %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
logging.info("Starting plotting...")
if args.get("debug"):
    logging.getLogger().setLevel(logging.DEBUG)
logging.debug("ARGS: {0}".format(args))

# Check that file at path exists and ends in .json
if not os.path.exists(args['path']):
    logging.warning("Given path does not exist! Exiting...")
    sys.exit(1)
if not os.path.split(args['path'])[-1].endswith('.json'):
    logging.warning("Given path does not point to a .json file! Exiting...")
    sys.exit(1)

# Read position data from file
logging.info("Reading position data...")
objects = []
canvas = {}
with open(args['path']) as fp:
    data = json.load(fp)
    objects = data['objects']
    canvas = data['canvas']
    
# Calculate activity
logging.info("Calculating activity...")
objects_activity = []
interval = 1
if args['interval']:
    interval = args['interval']
for obj in objects:
    o = { 't': [], 'A': [] }
    for i in range(0, len(obj['X']), interval):
        if i - interval < 0:
            o['t'].append(i)
            o['A'].append(0)
        else:
            o['t'].append(i)
            o['A'].append(dist(obj['X'][i], obj['Y'][i], obj['X'][i-interval], obj['Y'][i-interval]))
    objects_activity.append(o)

# Set up plots
logging.info("Setting up plots...")
fig, ax = plt.subplots()
for i, obj in enumerate(objects_activity):
    # Plot scatter of t/A
    plt.plot(obj['t'], obj['A'])

plt.title("Activity over Time ({0} frame interval)".format(interval))
plt.xlabel("Time (frames)")
plt.ylabel("Activity")
plt.legend()
plt.show()

if input("Save figure? ").lower() in ('y', 'yes'):
    logging.info("Saving figure...")
    plt.tight_layout()
    fig.savefig("figure", dpi=144)