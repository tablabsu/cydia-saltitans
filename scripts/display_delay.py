#! python3
import sys, os, argparse, logging, json, math
from matplotlib import pyplot as plt

DEFAULT_THRESHOLD = 0.1

# --------- UTILITY METHODS --------- 

# Returns distance between points
def dist(x1, y1, x2, y2):
    return math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2))

# -----------------------------------

# Setting up argument parser
parser = argparse.ArgumentParser(description="Display probability distribution of delays between jumps from json position data files")
parser.add_argument("path", help="Path to file containing position data")
parser.add_argument("-t", "--threshold", type=float, help="Threshold of activity, defaults to {0}".format(DEFAULT_THRESHOLD))
parser.add_argument("-o", "--objects", help="Index of objects to calculate delays for, accepts comma-separated list of indices")
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

# Loading position data from file
logging.info("Loading position data...")
objects = []
with open(args['path']) as fp:
    data = json.load(fp)
    objects = data['objects']

obj_i = []
if args['objects']:
    obj_i = [int(i) for i in args['objects'].split(",")]
else:
    obj_i = range(len(objects))

# Calculating delays
logging.info("Calculating delays...")
threshold = args['threshold']
if not threshold:
    threshold = DEFAULT_THRESHOLD
obj_delays = []
for o in obj_i:
    x = objects[o]['X']
    y = objects[o]['Y']
    d = 0
    delays = []
    for i in range(len(x) - 1):
        disp = dist(x[i], y[i], x[i+1], y[i+1])
        if disp <= threshold:
            d += 1
        else:
            delays.append(d)
            d = 0
    obj_delays.append(delays)

# Setting up plots
logging.info("Setting up plots...")
fig, ax = plt.subplots()
ax.set_title("Delay Distribution Histogram")
ax.set_xlabel("Delay (frames)")
ax.set_ylabel("Frequency")
for i, d in enumerate(obj_delays):
    bins = 1
    if len(d) > 0:
        bins = max(d)
    plt.hist(d, bins=bins, label="Object {0}".format(i))
if len(obj_delays) > 1:
    plt.legend()
plt.show()

# Saving figure
if input("Save figure? ").lower() in ('y', 'yes'):
    logging.info("Saving figure...")
    fig.savefig("figure")




