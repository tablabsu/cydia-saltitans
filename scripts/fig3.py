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

# Setting up argument parser
parser = argparse.ArgumentParser(description='Display probability distribution of delays between jumps and relative displacement frames from position data referenced in provided manifest file')
parser.add_argument('path', help='Path to manifest file')
parser.add_argument("-t", "--threshold", type=float, help="Threshold of activity, defaults to {0}".format(DEFAULT_THRESHOLD))
parser.add_argument("-mdf", "--min-delay-frames", type=float, help="Coefficient for minimum threshold for number of frames between delays to be plotted, usually 1.0, so minimum delay frames is 1.0 * CLIP_FPS")
parser.add_argument("-g", "--gen-individual", action="store_true", help="Generate individual delay and displacement plots for each dataset, saved in separate folders")
parser.add_argument("-hd", "--hardcoded-dist", action="store_true", help="Use the hard-coded distribution for delay/displacement")
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
total_ang_disps = []
for set in datasets:
    logging.info("Processing set '{0}'...".format(set))
    set_files = [f for f in manifest if f['set'] == set]
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
        threshold = args['threshold']
        if threshold is None:
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
        
        '''
        # Calculating angular displacements
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

                total_ang_disps.append(theta)
        '''
        '''
        # Calculating angular displacements (with delay/disp thresholding)
        last_v_i = 0
        last_v = None
        for i in range(len(x) - 1):
            # Take jump as 2D vector centered on origin
            v = [x[i+1] - x[i], y[i+1] - y[i]]
            # Check if jump passes displacement and delay threshold
            if mag(v) > threshold and (i - last_v_i + 1) >= int(mdf * fps):
                if last_v is None:
                    # If no previous jump recorded, save
                    last_v = v
                    last_v_i = i
                else:
                    # If previous jump recorded, use dot product to calculate angular disp
                    theta = math.acos(clamp(np.dot(last_v, v) / (mag(last_v)*mag(v)), -1, 1))
                    # If dot(last_v, rot90CCW(v)) > 0, change is to the right and theta must be reflected
                    if (last_v[0] * -v[1] + last_v[1] * v[0]) > 0:
                        theta = (2 * math.pi) - theta
                    total_ang_disps.append(theta)
                    # Update last jump
                    last_v = v
                    last_v_i = i
        '''

        logging.info("    Found {} delays, {} displacements, and {} angular displacements.".format(len(delays), len(disps), len(ang_disps)))
        
        # Convert all delays into seconds so clips w/ varying FPS values can be compared
        delays = [int(d / fps) for d in delays]

        set_delays.extend(delays)
        set_disps.extend(disps)
        set_ang_disps.extend(ang_disps)
        
    
    if args.get("gen_individual"):
        setname = set.replace("/", "_")
        
        with plt.style.context('science'):
        # Generate and save delay plot
            fig, ax = plt.subplots()
            ax.set_xlabel(r'$t_D$ (s)')
            ax.set_ylabel(r'P($t_D$)')
            ax.set_xlim(0, 25)
            plt.hist(set_delays, density=True, bins=max(set_delays), color=(0, 0, 0), histtype="step")
            fig.savefig("saved-delays/{0}_delays".format(setname))
            plt.close()

            # Generate and save displacement plot
            fig, ax = plt.subplots()
            ax.set_xlabel("δ ({0})".format(units))
            ax.set_ylabel("P(δ)")
            ax.set_xlim(0, 1.0)
            plt.hist(set_disps, density=True, bins=40, color=(0, 0, 0), histtype="step")
            fig.savefig("saved-disps/{0}_disps".format(setname))
            plt.close()

    total_delays.extend(set_delays)
    total_disps.extend(set_disps)
    total_ang_disps.extend(set_ang_disps)

logging.debug("Total Delays: {0}".format(len(total_delays)))
logging.debug("Total Displacements: {0}".format(len(total_disps)))
logging.info("Setting up plots...")

# Delay plot

'''

# Setting up plot
logging.info("Plotting {0} delays...".format(len(total_delays)))
#rcp.update({'font.size': 24})
fig, ax = plt.subplots()
ax.set_xlabel(r'$t_D$ (seconds)')
ax.set_ylabel(r'P($t_D$)')
ax.set_xlim(0, 25)
d = [i for i in total_delays if i <= 25 and i >= mdf]
hist, bins, _ = plt.hist(d, density=True, bins=max(d), color=(0, 0, 0), histtype='step')

# Fit distribution and plot
if not args.get("hardcoded_dist"):
    params = st.invgamma.fit(d + [0])
    logging.info("Delay fit parameters: {0}".format(params))
    fit_x = [i/10 for i in list(range(0, 250))]
    best_fit = st.invgamma.pdf(fit_x, *params)
    plt.plot(fit_x, best_fit, color=(1, 0, 0))
else:
    fit_x = [i/10 for i in list(range(0, 250))]
    best_fit = st.invgamma.pdf(fit_x, 1.7239, loc=-0.0667, scale=3.5195)
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
#rcp.update({'font.size': 24})
fig, ax = plt.subplots()
ax.set_xlabel("δ ({0})".format(units))
ax.set_ylabel("P(δ)")
ax.set_xlim(0, 1.0)
d = total_disps
hist, bins, _ = plt.hist(d, density=True, bins=40, color=(0, 0, 0), histtype='step')

# Fit distribution and plot
if not args.get("hardcoded_dist"):
    params = st.expon.fit(d)
    logging.info("Displacement fit parameters: {0}".format(params))
    fit_x = [i/100 for i in list(range(math.ceil(min(d) * 100), 100))]
    best_fit = st.expon.pdf(fit_x, *params)
    plt.plot(fit_x, best_fit, color=(1, 0, 0))
else:
    fit_x = [i/100 for i in list(range(math.ceil(min(d) * 100), 100))]
    best_fit = st.expon.pdf(fit_x, 0.1, 0.2556)
    plt.plot(fit_x, best_fit, color=(1, 0, 0))

# Show plot
plt.show()

# Save figure
if input("Save figure? ").lower() in ('y', 'yes'):
    logging.info("Saving figure...")
    fig.savefig("figure-displacement")
    fig.savefig("figure-displacement.svg", format="svg")

'''

with plt.style.context('science'):
    fig = plt.figure(constrained_layout=True, figsize=(3.5 * 3, 2.625 * 2))
    subfigs = fig.subfigures(2, 1)
    topAxs = subfigs[0].subplots(2, 1)
    btmAxs = subfigs[1].subplots(1, 3)
    topAxs = topAxs.flatten()
    btmAxs = btmAxs.flatten()
    # ---- TOP AXES
    data = np.genfromtxt("2021-08-13-video1-vidtimes.csv", delimiter = ',')
    delta_plot = np.array([0])
    video_time_plot = np.array([0])
    for j in range(60):#len(data)):
        delta_plot = np.append(delta_plot,0)
        delta_plot = np.append(delta_plot,data[j,1])
        delta_plot = np.append(delta_plot,0)
        video_time_plot = np.append(video_time_plot,data[j,2])
        video_time_plot = np.append(video_time_plot,data[j,2])
        video_time_plot = np.append(video_time_plot,data[j,2])
    delta_plot = delta_plot/np.max(delta_plot)
    topAxs[0].plot(video_time_plot,delta_plot,'-k')
    topAxs[0].set_xlim([-5,361])
    topAxs[0].set_xlabel('time (s)')
    topAxs[0].set_ylabel(r' $\delta$ / $\delta_m$')
    topAxs[0].text(-0.05, 0.95, "a", transform=topAxs[0].transAxes)

    delay_plot = np.array([0])
    delay_plot = np.append(delay_plot,data[0,0])
    video_time_plot2 = np.array([0])
    video_time_plot2 = np.append(video_time_plot2,0)

    for j in range(60):
        delay_plot = np.append(delay_plot,data[j,0])
        delay_plot = np.append(delay_plot,data[j,0])
        delay_plot = np.append(delay_plot,data[j+1,0])
        video_time_plot2 = np.append(video_time_plot2,data[j,2])
        video_time_plot2 = np.append(video_time_plot2,data[j,2])  
        video_time_plot2 = np.append(video_time_plot2,data[j,2])
    delay_plot = delay_plot/np.max(delay_plot)
    topAxs[1].plot(video_time_plot2,delay_plot,'-k')
    topAxs[1].set_xlim([-5,361])
    topAxs[1].set_xlabel('time (s)')
    topAxs[1].set_ylabel(r'$t_D$ / $t_{D,m}$')
    topAxs[1].text(-0.05, 0.95, "b", transform=topAxs[1].transAxes)


    # ---- BOTTOM AXES
    # delay
    btmAxs[0].set_xlabel(r'$t_D$ (s)')
    btmAxs[0].set_ylabel(r'P($t_D$)')
    btmAxs[0].set_xlim(0, 25)
    btmAxs[0].text(-0.15, 0.95, "c", transform=btmAxs[0].transAxes)
    d = [i for i in total_delays if i <= 25 and i >= mdf]
    print(f'Delays: {len(d)}')
    hist, bins, _ = btmAxs[0].hist(d, density=True, bins=max(d), color=(0, 0, 0), histtype='step')
    # delay fit
    params = st.invgamma.fit(d + [0])
    logging.info("Delay fit parameters: {0}".format(params))
    fit_x = [i/10 for i in list(range(0, 250))]
    best_fit = st.invgamma.pdf(fit_x, *params)
    btmAxs[0].plot(fit_x, best_fit, color=(1, 0, 0))
    # disp
    btmAxs[1].set_xlabel(r'$\delta$ ' + "({0})".format(units))
    btmAxs[1].set_ylabel(r'P($\delta$)')
    btmAxs[1].set_xlim(0, 1.0)
    btmAxs[1].text(-0.15, 0.95, "d", transform=btmAxs[1].transAxes)
    d = total_disps
    print(f'Displacements: {len(d)}')
    hist, bins, _ = btmAxs[1].hist(d, density=True, bins=40, color=(0, 0, 0), histtype='step')
    # disp fit
    params = st.expon.fit(d)
    logging.info("Displacement fit parameters: {0}".format(params))
    fit_x = [i/100 for i in list(range(math.ceil(min(d) * 100), 100))]
    best_fit = st.expon.pdf(fit_x, *params)
    btmAxs[1].plot(fit_x, best_fit, color=(1, 0, 0))
    # ang 
    btmAxs[2].remove()
    btmAxs[2] = subfigs[1].add_subplot(1, 3, 3, projection='polar')
    btmAxs[2].set_theta_zero_location('N')
    btmAxs[2].set_xticklabels(["0° (Forwards)", "45°", "90°", "135°", "180° (Backwards)", "225°", "270°", "315°"])
    btmAxs[2].set_rticks([0.05, 0.15, 0.25])
    btmAxs[2].set_rlabel_position(0)
    btmAxs[2].text(-0.15, 0.95, "e", transform=btmAxs[2].transAxes)
    vals, bins, _ = btmAxs[2].hist(total_ang_disps, density=True, histtype='step', bins=30, color=(0, 0, 0))
    print(f'Ang Disp:\n\tVals: {"[" + ",".join([str(v) for v in vals]) +"]"}\n\tBins: {"[" + ",".join([str(b) for b in bins]) + "]"}')
    print(f'Angular displacements: {len(total_ang_disps)}')
    # show/save
    plt.show()
    if input("Save figure? ").lower() in ('y', 'yes'):
        logging.info("Saving figure...")
        fig.savefig("fig-dists", dpi=300)