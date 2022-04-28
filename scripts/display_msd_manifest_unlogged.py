#! python3
import sys, os, argparse, logging, json, math
import numpy as np
from random import random
from matplotlib import pyplot as plt
from matplotlib import rcParams as rcp

# --------- UTILITY METHODS --------- 

# Returns distance between points
def dist(x1, y1, x2, y2):
    return math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2))

def fit_poly_through_origin(x, y, n=1):
    a = x[:, np.newaxis] ** np.arange(1, n+1)
    coeff = np.linalg.lstsq(a, y)[0]
    return np.concatenate(([0], coeff))

# -----------------------------------

# Setting up argument parser
parser = argparse.ArgumentParser(description="Display mean-squared displacement (MSD) plots from position data files linked in manifest file")
parser.add_argument("path", help="Path to manifest file, contains paths to data files and properties associated")
parser.add_argument("-ns", "--no-scatter", action='store_true', help="Disables showing scatter plots")
parser.add_argument("-l", "--legend", action='store_true', help='Show legend on resulting plot')
parser.add_argument("-d", "--debug", action="store_true", help="Show debug information")
args = vars(parser.parse_args())

# Setting up logger
format = "%(levelname)s : %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
logging.info("Starting MSD calculation...")
if args.get("debug"):
    logging.getLogger().setLevel(logging.DEBUG)
logging.debug("ARGS: {0}".format(args))

# Check that file at path exists and ends in .json
if not os.path.exists(args['path']):
    logging.warning("Given path does not exist! Exiting...")
    sys.exit(1)
if not os.path.split(args['path'])[-1].endswith(".json"):
    logging.warning("Given path does not point to a .json file! Exiting...")
    sys.exit(1)

# Load manifest
logging.info("Loading manifest file...")
manifest = []
with open(args['path']) as fp:
    manifest = json.load(fp)
datasets = list(set([f['set'] for f in manifest]))
datasets.sort()
logging.debug("Datasets: {0}".format(datasets))
logging.debug("Number of datasets: {0}".format(len(datasets)))

sets_msd = []
for set in datasets:
    logging.info("Processing set '{0}'...".format(set))
    set_files = [f for f in manifest if f['set'] == set]
    logging.debug("Set files: {0}".format([os.path.split(p['path'])[-1] for p in set_files]))
    
    fps = set_files[0]['fps']
    tau_lim = set_files[0]['tau_limit']

    # Calculate squared displacements
    set_msd = { 'set': set, 'fps': fps, 'tau_limit': tau_lim, 'tau': [], 'msd': [] }
    for f in set_files:
        logging.info("    Processing file '{0}'...".format(os.path.split(f['path'])[-1]))
        set_data = {}
        with open(f['path']) as fp:
            set_data = json.load(fp)
        tau = range(1, int(len(set_data['objects'][0]['X']) / 2))
        for t in tau:
            # Pull out X and Y coordinate lists
            tau_x = set_data['objects'][0]['X']
            tau_y = set_data['objects'][0]['Y']

            # Calculate distance between points apart by interval tau, then square displacement
            tau_dist = [dist(tau_x[i], tau_y[i], tau_x[i+t], tau_y[i+t]) for i in range(len(tau_x) - t)]
            tau_dist = [i**2 for i in tau_dist]

            set_msd['tau'].append(t)
            set_msd['msd'].append(tau_dist)

    # Merge squared displacements and convert to mean squared displacement
    tau = []
    msd = []
    for t in range(1, max(set_msd['tau'])):
        sd = []
        for i, u in enumerate(set_msd['tau']):
            if t == u:
                sd.extend(set_msd['msd'][i])
        if len(sd) > 0:
            msd_val = sum(sd) / len(sd)
            tau.append(t)
            msd.append(msd_val)
    set_msd['tau'] = tau
    set_msd['msd'] = msd

    sets_msd.append(set_msd)

# Set up plot
logging.info("Setting up plot...")
fig, ax = plt.subplots()
msd_slopes = []
for i, set in enumerate(sets_msd):
    tau = set['tau']
    msd = set['msd']

    # Convert to seconds
    tau = [t * (1 / set['fps']) for t in tau]

    # Apply tau limit
    lim_tau = []
    lim_msd = []
    unlim_tau = []
    unlim_msd = []
    if set['tau_limit'] > 0:
        tl = set['tau_limit']
        for k in range(len(tau)):
            if tau[k] <= tl:
                lim_tau.append(tau[k])
                lim_msd.append(msd[k])
            else:
                unlim_tau.append(tau[k])
                unlim_msd.append(msd[k])
    else:
        lim_tau = tau
        lim_msd = msd
    
    # Set random color
    color = (random(), random(), random())

    # Plot scatter of lim and unlim tau
    if not args['no_scatter']:
        plt.scatter(lim_tau, lim_msd, marker=',', color=color, s=(288./fig.dpi)**2)

    # Set MSD line type
    line_type = '--'
    if args['no_scatter']:
        line_type = '-'

    # Plot trendlines of log tau/msd
    #log_lim_tau = np.log10(lim_tau)
    #log_lim_msd = np.log10(lim_msd)
    pf = np.polyfit(lim_tau, lim_msd, 1)
    p = np.poly1d(pf)
    msd_slopes.append(pf[0])
    plt.plot(lim_tau, p(lim_tau), line_type, label='{0} : Slope {1:.2f}'.format(set['set'], pf[0]), color=color)

plt.xlabel("τ (sec)")
plt.ylabel("MSD (cm²)")
if args['legend']:
    plt.legend(prop={ 'size': 6 })
plt.tight_layout()
plt.show()

logging.info("MSD Slope: {0}".format(round(msd_slopes[0], 5)))

#if input("Save figure? ").lower() in ('y', 'yes'):
#    logging.info("Saving figure...")
#    fig.savefig("figure-msd.png")
