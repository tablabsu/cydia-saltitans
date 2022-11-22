#! python3
import sys, os, argparse, logging, json, math
from random import random
from matplotlib import pyplot as plt
from matplotlib import rcParams as rcp
from scipy import stats as st
import numpy as np

DEFAULT_THRESHOLD = 0.1
MINIMUM_DELAY_FRAMES = 1.0

# --------- UTILITY METHODS --------- 

# Returns distance between points
def dist(x1, y1, x2, y2):
    return math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2))

# Returns vector magnitude
def mag(x):
    return math.sqrt(sum(i**2 for i in x))

# Clamps value to range
def clamp(n, min_val, max_val):
    return max(min(n, max_val), min_val)

# -----------------------------------

paper_path = "../experiments/manifests/paper.json"
sandpaper_path = "../experiments/manifests/sandpaper.json"

mdf = MINIMUM_DELAY_FRAMES

logging.info("Loading manifest file...")
paper_manifest = []
sandpaper_manifest = []
with open(paper_path) as fp:
    paper_manifest = json.load(fp)
with open(sandpaper_path) as fp:
    sandpaper_manifest = json.load(fp)
paper_datasets = list(set([f['set'] for f in paper_manifest]))
paper_datasets.sort()
sandpaper_datasets = list(set([f['set'] for f in sandpaper_manifest]))
sandpaper_datasets.sort()

units = None
paper_total_delays = []
paper_total_disps = []
paper_total_ang_disps = []
for set in paper_datasets:
    logging.info("Processing set '{0}'...".format(set))
    set_files = [f for f in paper_manifest if f['set'] == set]
    logging.debug("Set files: {0}".format([os.path.split(p['path'])[-1] for p in set_files]))
    set_delays = []
    set_disps = []
    set_ang_disps = []
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
        logging.info("    Calculating delays & displacements...")
        threshold = DEFAULT_THRESHOLD
        delays = []
        disps = []
        ang_disps = []
        x = objects[0]['X']
        y = objects[0]['Y']
        last_v = None
        d = 1
        for i in range(len(x) - 1):
            disp = dist(x[i], y[i], x[i+1], y[i+1])
            if disp < threshold:
                d += 1
            else:
                if d >= int(mdf * fps):
                    v = [x[i+1] - x[i], y[i+1] - y[i]]
                    if last_v is None:
                        last_v = v
                    else:
                        # Use dot product to calculate angular disp
                        theta = math.acos(clamp(np.dot(last_v, v) / (mag(last_v)*mag(v)), -1, 1))
                        # If dot(last_v, rot90CCW(v)) > 0, change is to the right and theta must be reflected
                        if (last_v[0] * -v[1] + last_v[1] * v[0]) > 0:
                            theta = (2 * math.pi) - theta
                        ang_disps.append(theta)
                        last_v = v
                    delays.append(d)
                    disps.append(disp)
                    d = 1

        logging.info("    Found {} delays and {} displacements.".format(len(delays), len(disps)))
        
        # Convert all delays into seconds so clips w/ varying FPS values can be compared
        delays = [int(d / fps) for d in delays]

        set_delays.extend(delays)
        set_disps.extend(disps)
        set_ang_disps.extend(ang_disps)
    
    paper_total_delays.extend(set_delays)
    paper_total_disps.extend(set_disps)
    paper_total_ang_disps.extend(set_ang_disps)

units = None
sandpaper_total_delays = []
sandpaper_total_disps = []
sandpaper_total_ang_disps = []
for set in sandpaper_datasets:
    logging.info("Processing set '{0}'...".format(set))
    set_files = [f for f in sandpaper_manifest if f['set'] == set]
    logging.debug("Set files: {0}".format([os.path.split(p['path'])[-1] for p in set_files]))
    set_delays = []
    set_disps = []
    set_ang_disps = []
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
        logging.info("    Calculating delays & displacements...")
        threshold = DEFAULT_THRESHOLD
        delays = []
        disps = []
        ang_disps = []
        x = objects[0]['X']
        y = objects[0]['Y']
        last_v = None
        d = 1
        for i in range(len(x) - 1):
            disp = dist(x[i], y[i], x[i+1], y[i+1])
            if disp < threshold:
                d += 1
            else:
                if d >= int(mdf * fps):
                    v = [x[i+1] - x[i], y[i+1] - y[i]]
                    if last_v is None:
                        last_v = v
                    else:
                        # Use dot product to calculate angular disp
                        theta = math.acos(clamp(np.dot(last_v, v) / (mag(last_v)*mag(v)), -1, 1))
                        # If dot(last_v, rot90CCW(v)) > 0, change is to the right and theta must be reflected
                        if (last_v[0] * -v[1] + last_v[1] * v[0]) > 0:
                            theta = (2 * math.pi) - theta
                        ang_disps.append(theta)
                        last_v = v
                    delays.append(d)
                    disps.append(disp)
                    d = 1

        logging.info("    Found {} delays and {} displacements.".format(len(delays), len(disps)))
        
        # Convert all delays into seconds so clips w/ varying FPS values can be compared
        delays = [int(d / fps) for d in delays]

        set_delays.extend(delays)
        set_disps.extend(disps)
        set_ang_disps.extend(ang_disps)

    sandpaper_total_delays.extend(set_delays)
    sandpaper_total_disps.extend(set_disps)
    sandpaper_total_ang_disps.extend(set_ang_disps)

with plt.style.context('science'):
    fig, axs = plt.subplots(1, 2, figsize=(3.5 * 2, 2.625))
    axs = axs.flatten()
    # delay
    axs[0].set_title("Paper")
    axs[0].set_xlabel(r'$t_D$ (s)')
    axs[0].set_ylabel(r'P($t_D$)')
    axs[0].set_xlim(0, 25)
    axs[0].text(-0.15, 0.95, "a", transform=axs[0].transAxes)
    d = [i for i in paper_total_delays if i <= 25 and i >= mdf]
    hist, bins, _ = axs[0].hist(d, density=True, bins=max(d), color=(0, 0, 0), histtype='step')
    # delay fit
    params = st.invgamma.fit(d + [0])
    logging.info("Delay fit parameters: {0}".format(params))
    fit_x = [i/10 for i in list(range(0, 250))]
    best_fit = st.invgamma.pdf(fit_x, *params)
    axs[0].plot(fit_x, best_fit, color=(1, 0, 0))
    # disp
    axs[1].set_title("Sandpaper")
    axs[1].set_xlabel(r'$t_D$ (s)')
    axs[1].set_ylabel(r'P($t_D$)')
    axs[1].set_xlim(0, 25)
    axs[1].text(-0.15, 0.95, "b", transform=axs[1].transAxes)
    d = [i for i in sandpaper_total_delays if i <= 25 and i >= mdf]
    hist, bins, _ = axs[1].hist(d, density=True, bins=max(d), color=(0, 0, 0), histtype='step')
    # delay fit
    params = st.invgamma.fit(d + [0])
    logging.info("Delay fit parameters: {0}".format(params))
    fit_x = [i/10 for i in list(range(0, 250))]
    best_fit = st.invgamma.pdf(fit_x, *params)
    axs[1].plot(fit_x, best_fit, color=(1, 0, 0))
    plt.show()
    if input("Save figure? ").lower() in ('y', 'yes'):
        logging.info("Saving figure...")
        fig.savefig("supp-fig-dists-delay", dpi=300)

with plt.style.context('science'):
    fig, axs = plt.subplots(1, 2, figsize=(3.5 * 2, 2.625))
    axs = axs.flatten()
    # disp
    axs[0].set_title("Paper")
    axs[0].set_xlabel(r'$\delta$ ' + "({0})".format(units))
    axs[0].set_ylabel(r'P($\delta$)')
    axs[0].set_xlim(0, 1.0)
    axs[0].text(-0.15, 0.95, "a", transform=axs[0].transAxes)
    d = paper_total_disps
    hist, bins, _ = axs[0].hist(d, density=True, bins=40, color=(0, 0, 0), histtype='step')
    # disp fit
    params = st.expon.fit(d)
    logging.info("Displacement fit parameters: {0}".format(params))
    fit_x = [i/100 for i in list(range(math.ceil(min(d) * 100), 100))]
    best_fit = st.expon.pdf(fit_x, *params)
    axs[0].plot(fit_x, best_fit, color=(1, 0, 0))
    # disp
    axs[1].set_title("Sandpaper")
    axs[1].set_xlabel(r'$\delta$ ' + "({0})".format(units))
    axs[1].set_ylabel(r'P($\delta$)')
    axs[1].set_xlim(0, 1.0)
    axs[1].text(-0.15, 0.95, "b", transform=axs[1].transAxes)
    d = sandpaper_total_disps
    hist, bins, _ = axs[1].hist(d, density=True, bins=40, color=(0, 0, 0), histtype='step')
    # disp fit
    params = st.expon.fit(d)
    logging.info("Displacement fit parameters: {0}".format(params))
    fit_x = [i/100 for i in list(range(math.ceil(min(d) * 100), 100))]
    best_fit = st.expon.pdf(fit_x, *params)
    axs[1].plot(fit_x, best_fit, color=(1, 0, 0))
    plt.show()
    if input("Save figure? ").lower() in ('y', 'yes'):
        logging.info("Saving figure...")
        fig.savefig("supp-fig-dists-disp", dpi=300)

with plt.style.context('science'):
    fig, axs = plt.subplots(1, 2, figsize=(3.5 * 2, 2.625), subplot_kw={'projection' : 'polar'})
    axs = axs.flatten()
    axs[0].set_title("Paper")
    axs[0].set_theta_zero_location('N')
    axs[0].set_xticklabels(["0° (Forwards)", "45°", "90°", "135°", "180° (Backwards)", "225°", "270°", "315°"])
    axs[0].set_rticks([0.05, 0.15, 0.25, 0.35])
    axs[0].set_rlabel_position(0)
    axs[0].text(-0.15, 0.95, 'a', transform=axs[0].transAxes)
    axs[0].hist(paper_total_ang_disps, density=True, histtype='step', bins=30, color=(0, 0, 0))
    axs[1].set_title("Sandpaper")
    axs[1].set_theta_zero_location('N')
    axs[1].set_xticklabels(["0° (Forwards)", "45°", "90°", "135°", "180° (Backwards)", "225°", "270°", "315°"])
    axs[1].set_rticks([0.05, 0.15, 0.25, 0.35])
    axs[1].set_rlabel_position(0)
    axs[1].text(-0.15, 0.95, 'b', transform=axs[1].transAxes)
    axs[1].hist(sandpaper_total_ang_disps, density=True, histtype='step', bins=30, color=(0, 0, 0))
    plt.show()
    if input("Save figure? ").lower() in ('y', 'yes'):
        logging.info("Saving figure...")
        fig.savefig("supp-fig-dists-ang", dpi=300)