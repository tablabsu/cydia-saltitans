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
parser = argparse.ArgumentParser(description="Display mean-squared displacemnt (MSD) plots from position data files")
parser.add_argument("path", help="Path to file containing position data")
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
if not os.path.exists(args["path"]):
    logging.warning("Given path does not exist! Exiting...")
    sys.exit(1)
if not os.path.split(args["path"])[-1].endswith(".json"):
    logging.warning("Given path does not point to a .json file! Exiting...")
    sys.exit(1)

objects = []
canvas = {}
# Read position data from file
logging.info("Reading position data...")
with open(args['path']) as fp:
    data = json.load(fp)
    objects = data["objects"]
    canvas = data['canvas']

# Calculate MSD data from objects
logging.info("Calculating MSD data...")
objects_msd = []
for obj in objects:
    o = { 'tau': [], 'msd': [] }
    tau = range(1, int(len(obj['X']) / 2))
    for t in tau:
        # Pull out X and Y coordinate lists
        tau_x = obj['X']
        tau_y = obj['Y']

        # Calculate distance between points apart by interval tau, then square displacement
        tau_dist = [dist(tau_x[i], tau_y[i], tau_x[i+t], tau_y[i+t]) for i in range(len(tau_x) - t)]
        tau_dist = [math.pow(i, 2) for i in tau_dist]

        # Average the displacement of those intervals
        msd = sum(tau_dist) / len(tau_dist)

        # Add to object's tau and msd list
        o['tau'].append(t)
        o['msd'].append(msd)
    objects_msd.append(o)

# Set up plots
logging.info("Setting up plots...")
fig, ax = plt.subplots()
for i, obj in enumerate(objects_msd):
    # Calculate natural log of tau and msd
    tau = [math.log(i) if i != 0 else i for i in obj['tau']]
    msd = [math.log(i) if i != 0 else i for i in obj['msd']]

    # Plot scatter of log tau/msd
    plt.scatter(tau, msd)

    # Plot trendlines of log tau/msd
    pf = np.polyfit(tau, msd, 1)
    p = np.poly1d(pf)
    plt.plot(tau, p(tau), '--', label="Object {1} slope: {0:.2f}".format(pf[0], i))

plt.title("Log MSD over Log Tau")
plt.xlabel("Log Tau")
plt.ylabel("Log MSD ({0})".format(canvas['units'] + "^2"))
plt.legend()
plt.show()

if input("Save figure? ").lower() in ('y', 'yes'):
    logging.info("Saving figure...")
    plt.tight_layout()
    fig.savefig("figure", dpi=144)
