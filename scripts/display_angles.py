#! python3
import sys, os, argparse, logging, json, math
from random import random
from matplotlib import pyplot as plt

# --------- UTILITY METHODS --------- 

# Returns distance between points
def dist(x1, y1, x2, y2):
    return math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2))

# -----------------------------------

# Setting up argument parser
parser = argparse.ArgumentParser(description="Display angular displacement distribution of bean movements")
parser.add_argument("path", nargs='+', help="Path to position data file")
parser.add_argument("-d", "--debug", action="store_true", help="Show debug information")
parser.add_argument("-o", "--objects", help="Index of objects to calculate angular displacement for, accepts comma-separated list of indices")
args = vars(parser.parse_args())

# Starting logger for status info
format = "%(levelname)s : %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S") 
logging.info("Plotting angular displacement distribution...")
if args.get("debug"):
    logging.getLogger().setLevel(logging.DEBUG)
logging.debug("ARGS: {0}".format(args)) # DEBUG

total_disps = []
for p_num, path in enumerate(args['path']):
    
    # Check that file at path exists and ends in .json
    if not os.path.exists(path):
        logging.warning("Given path does not exist! Exiting...")
        sys.exit(1)
    if not os.path.split(path)[-1].endswith('.json'):
        logging.warning("Given path does not point to a .json file! Exiting...")
        sys.exit(1)
    
    # Loading position data from file
    logging.info("Loading position data for '{0}'...".format(path))
    objects = []
    canvas = {}
    with open(path) as fp:
        data = json.load(fp)
        objects = data['objects']
        canvas = data['canvas']
    
    # Filtering out specified objects
    obj_i = []
    if args['objects']:
        obj_i = [int(i) for i in args['objects'].split(',')]
    else:
        obj_i = range(len(objects))

    # Calculating angular displacements
    logging.info("Calculating angular displacements...")
    obj_disps = []
    for o in obj_i:
        x = objects[o]['X']
        y = objects[o]['Y']
        disps = []
        for i in range(len(x) - 2):
            # Calculating lengths of AB, BC, CA
            a = dist(x[i], y[i], x[i+1], y[i+1])
            b = dist(x[i+1], y[i+1], x[i+2], y[i+2])
            c = dist(x[i+2], y[i+2], x[i], y[i])

            if a > 0 and b > 0 and c > 0:
                # Law of cosines: theta = acos( ( a^2 + b^2 - c^2 ) / ( 2ab ))
                theta = math.acos(round((a**2 + b**2 - c**2) / (2 * a * b), 4))

                # Checking slopes for displacement changes
                sab = 0
                sac = 0
                # Set defined value for undefined slope
                if x[i+1] - x[i] != 0:
                    sab = (y[i+1] - y[i]) / (x[i+1] - x[i])
                else:
                    sab = 10000000
                if x[i+2] - x[i+1] != 0:
                    sbc = (y[i+2] - y[i+1]) / (x[i+2] - x[i+1])
                else:
                    sbc = 10000000

                # If slope change is negative, angle should be reflected
                if sbc < sab:
                    theta = (2 * math.pi) - theta

                disps.append(theta)
        obj_disps.append(disps)
    
    for i, o in enumerate(obj_disps):
        if p_num == 0:
            total_disps.append(o)
        else:
            total_disps[i].extend(o)

logging.info("Setting up plots...")

# Reversing values so 0 deg = forward, 180 deg = backward
obj_disps = [[(d - math.pi) if (d + math.pi) >= (2*math.pi) else (d + math.pi) for d in obj ] for obj in obj_disps]
color = (random(), random(), random())

# Setting up angular disp. plot
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
#ax.set_title("Angular Displacement Distribution")
ax.set_theta_zero_location('N')
ax.set_xticklabels(["0° (Forwards)", "45°", "90°", "135°", "180° (Backwards)", "225°", "270°", "315°"])
ax.set_yticklabels([])
for i, d in enumerate(obj_disps):
    plt.hist(d, bins=30, label="Object {0}".format(i), color=color)
if len(obj_disps) > 1:
    plt.legend()
plt.show()

if input("Save figure? ").lower() in ('y', 'yes'):
    logging.info("Saving figure...")
    fig.savefig("figure-angular-disp")
'''
fig, ax = plt.subplots()
for i, d in enumerate(obj_disps):
    plt.hist(d, bins=30, label="Object {0}".format(i), color=color)
if len(obj_disps) > 1:
    plt.legend()
plt.show()

if input("Save figure? ").lower() in ('y', 'yes'):
    logging.info("Saving figure...")
    fig.savefig("figure-angular-disp-flat")
'''
