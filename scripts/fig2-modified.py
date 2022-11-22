import math
import os
from matplotlib import pyplot as plt
import json
from random import random
import numpy as np
from scipy import stats
import seaborn as sns


# ---------------------------------- POSITIONS ----------------------------------

pos_path = "../experiments/fig-test/pos_data_8000-8600.json"

# Read position data from file, move into correct format to display frames
frames = []
canvas = {}
with open(pos_path) as fp:
    data = json.load(fp)
    objects = data['objects']
    canvas = data['canvas']
    frames = [{ 'X': [], 'Y': [] } for i in range(len(objects[0]['X']))]
    for obj in objects:
        for frame in range(len(min([obj['X'], obj['Y']]))):
            frames[frame]['X'].append(obj['X'][frame])
            frames[frame]['Y'].append(obj['Y'][frame])

# Adding frame number to frames
for i in range(len(frames)):
    frames[i]["number"] = i + 1

# ---------------------------------- MSD - HOT ----------------------------------

# Returns distance between points
def dist(x1, y1, x2, y2):
    return math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2))

msd_path = "../experiments/manifests/hot-data.json"

hot_manifest = []
with open(msd_path) as fp:
    hot_manifest = json.load(fp)
hot_datasets = list(set([f['set'] for f in hot_manifest]))
hot_datasets.sort()

hot_sets_msd = []
for dset in hot_datasets:
    print("Processing set '{0}'...".format(dset))
    set_files = [f for f in hot_manifest if f['set'] == dset]
    
    fps = set_files[0]['fps']
    tau_lim = set_files[0]['tau_limit']

    # Calculate squared displacements
    set_msd = { 'set': dset, 'fps': fps, 'tau_limit': tau_lim, 'tau': [], 'msd': [] }
    for f in set_files:
        print("    Processing file '{0}'...".format(os.path.split(f['path'])[-1]))
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

    hot_sets_msd.append(set_msd)

# ---------------------------------- MSD - COLD ----------------------------------

msd_path = "../experiments/manifests/cold-data.json"

cold_manifest = []
with open(msd_path) as fp:
    cold_manifest = json.load(fp)
cold_datasets = list(set([f['set'] for f in cold_manifest]))
cold_datasets.sort()

cold_sets_msd = []
for dset in cold_datasets:
    print("Processing set '{0}'...".format(dset))
    set_files = [f for f in cold_manifest if f['set'] == dset]
    
    fps = set_files[0]['fps']
    tau_lim = set_files[0]['tau_limit']

    # Calculate squared displacements
    set_msd = { 'set': dset, 'fps': fps, 'tau_limit': tau_lim, 'tau': [], 'msd': [] }
    for f in set_files:
        print("    Processing file '{0}'...".format(os.path.split(f['path'])[-1]))
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

    cold_sets_msd.append(set_msd)

# ---------------------------------- DIFF CONST ----------------------------------

diff_path = "../misc/msd-size-plot/msd-slopes-unlogged.txt"
color_code = True

dataset = []
diff_msd = []
size = []
if color_code:
    hot_dataset = []
    cold_dataset = []
    hot_diff_msd = []
    cold_diff_msd = []
    hot_size = []
    cold_size = []
with open(diff_path) as fp:
    data = fp.readlines()
    for l in data:
        line = l.split(":")
        dataset.append(line[0])
        diff_msd.append(float(line[1]))
        size.append(float(line[2]))
        if color_code:
            if line[3].strip() == "hot":
                hot_dataset.append(line[0])
                hot_diff_msd.append(float(line[1]))
                hot_size.append(float(line[2]))
            elif line[3].strip() == "cold":
                cold_dataset.append(line[0])
                cold_diff_msd.append(float(line[1]))
                cold_size.append(float(line[2]))
            else:
                print(line[3])

diff_msd = [x / 4 for x in diff_msd]
if color_code:
    hot_diff_msd = [x / 4 for x in hot_diff_msd]
    cold_diff_msd = [x / 4 for x in cold_diff_msd]
    filtered_hot_diff_msd = [hot_diff_msd[i] for i in range(len(hot_diff_msd)) if hot_size[i] >= 7.5 and hot_size[i] <= 9.5]
    filtered_cold_diff_msd = [cold_diff_msd[i] for i in range(len(cold_diff_msd)) if cold_size[i] >= 7.5 and cold_size[i] <= 9.5]
res = stats.linregress(size, diff_msd)
if color_code:
    res = stats.linregress(hot_size, hot_diff_msd)
fit_line = np.poly1d([res.slope, res.intercept])
print(f'ttest_ind: {stats.ttest_ind(cold_diff_msd, hot_diff_msd)}')
print(f'2c fit results: {res}')

# ---------------------------------- DISPLAY ----------------------------------

with plt.style.context('science'):
    fig, axs = plt.subplots(2, 3, figsize=(3.5 * 3, 2.625 * 2))
    axs = axs.flatten()
    # -------- POSITION PLOT --------
    axs[0].set_xlim(0, canvas['width'])
    axs[0].set_ylim(canvas['height'], 0) 
    axs[0].set_xlabel("X position ({0})".format(canvas['units']))
    axs[0].set_ylabel("Y position ({0})".format(canvas['units']))
    for i in range(len(frames) - 1):
        for o in range(len(frames[i]['X'])):
            axs[0].plot([frames[i]['X'][o], frames[i + 1]['X'][o]], [frames[i]['Y'][o], frames[i+1]['Y'][o]], color=(0, 0, 0))
    x_pos = [f['X'][0] for f in frames]
    y_pos = [f['Y'][0] for f in frames]
    dist_pos = [math.sqrt(x_pos[i]**2 + y_pos[i]**2) for i in range(len(x_pos))]
    dist_stdev = np.std(dist_pos) * 2
    axs[0].set_xlim(min(x_pos) - dist_stdev, max(x_pos) + dist_stdev)
    axs[0].set_ylim(max(y_pos) + dist_stdev, min(y_pos) - dist_stdev)
    # -------- MSD PLOT (HOT) --------
    hot_alpha_vals = []
    for i, set in enumerate(hot_sets_msd):
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
        color = (random(), random(), random()) if len(hot_sets_msd) > 1 else (0, 0, 0)

        with plt.style.context('scatter'):
            axs[1].scatter(lim_tau, lim_msd, color=color)

        # Set MSD line type
        line_type = '--'

        # Plot trendlines of log tau/msd
        log_lim_tau = np.log10(lim_tau)
        log_lim_msd = np.log10(lim_msd)
        msd_res = stats.linregress(log_lim_tau, log_lim_msd)
        msd_fit_line = np.poly1d([msd_res.slope, msd_res.intercept])
        hot_alpha_vals.append(msd_res.slope)
        axs[1].plot(np.power(10, log_lim_tau), np.power(10, msd_fit_line(log_lim_tau)), line_type, label='{0} : Slope {1:.2f}'.format(set['set'], res.slope), color=color)
    axs[1].set_xlim(0.1, 1000)
    axs[1].set_ylim(0.0005, 100)
    axs[1].set_xlabel(r'$\tau$ (s)')
    axs[1].set_ylabel(r'MSD ($cm^2$)')
    axs[1].set_xscale('log')
    axs[1].set_yscale('log')
    axs[1].text(0.05, 0.9, r'$37.2^{\circ}C$', transform=axs[1].transAxes)
    # -------- MSD PLOT (COLD) --------
    cold_alpha_vals = []
    for i, set in enumerate(cold_sets_msd):
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
        color = (random(), random(), random()) if len(hot_sets_msd) > 1 else (0, 0, 0)

        with plt.style.context('scatter'):
            axs[2].scatter(lim_tau, lim_msd, color=color)

        # Set MSD line type
        line_type = '--'

        # Plot trendlines of log tau/msd
        log_lim_tau = np.log10(lim_tau)
        log_lim_msd = np.log10(lim_msd)
        msd_res = stats.linregress(log_lim_tau, log_lim_msd)
        msd_fit_line = np.poly1d([msd_res.slope, msd_res.intercept])
        cold_alpha_vals.append(msd_res.slope)
        axs[2].plot(np.power(10, log_lim_tau), np.power(10, msd_fit_line(log_lim_tau)), line_type, label='{0} : Slope {1:.2f}'.format(set['set'], res.slope), color=color)
    axs[2].set_xlim(0.1, 1000)
    axs[2].set_ylim(0.0005, 100)
    axs[2].set_xlabel(r'$\tau$ (s)')
    axs[2].set_ylabel(r'MSD ($cm^2$)')
    axs[2].set_xscale('log')
    axs[2].set_yscale('log')
    axs[2].text(0.05, 0.9, r'$26^{\circ}C$', transform=axs[2].transAxes)
    # -------- DIFF CONST PLOT --------
    axs[4].set_xlabel('L (mm)')
    axs[4].set_ylabel(r'D ($cm^{2}/s$)')
    with plt.style.context(['scatter']):
        if color_code:
            axs[4].scatter(hot_size, hot_diff_msd, color="red")
            axs[4].scatter(cold_size, cold_diff_msd, color="blue")
            sz = hot_size + cold_size
            lsp = np.linspace(min(sz), max(sz))
            axs[4].plot(lsp, fit_line(lsp), linestyle='--', color="red")
        else:
            axs[4].scatter(size, diff_msd, color='black')
            axs[4].plot(size, fit_line(size), linewidth=2, color=(1, 0, 0))
    # -------- SEABORN PLOTS --------
    pal = {"cold" : "b", "hot" : "r"}
    alphax = ['cold'] * len(cold_alpha_vals) + ['hot'] * len(hot_alpha_vals)
    alphay = cold_alpha_vals + hot_alpha_vals
    sns.boxplot(alphax, alphay, ax=axs[3], color="white", showfliers=False, palette=pal)
    sns.swarmplot(alphax, alphay, ax=axs[3], color="black", size=4)
    axs[3].set_ylabel(r'$\alpha$')
    axs[3].set_xticklabels([r'$26^{\circ}C$', r'$37.2^{\circ}C$'])
    print(f'Cold diff msd <{len(cold_diff_msd)}> -> <{len(filtered_cold_diff_msd)}>')
    print(f'Hot diff msd <{len(hot_diff_msd)}> -> <{len(filtered_hot_diff_msd)}>')
    diffx = ['cold'] * len(filtered_cold_diff_msd) + ['hot'] * len(filtered_hot_diff_msd)
    diffy = filtered_cold_diff_msd + filtered_hot_diff_msd
    sns.boxplot(diffx, diffy, ax=axs[5], color="white", showfliers=False, palette=pal)
    sns.swarmplot(diffx, diffy, ax=axs[5], color="black", size=4)
    axs[5].set_ylabel(r'D ($cm^{2}/s$)')
    axs[5].set_xticklabels([r'$26^{\circ}C$', r'$37.2^{\circ}C$'])
    # -------- DISPLAY/SAVE --------
    axs[0].text(-0.2, 0.95, 'a', transform=axs[0].transAxes)
    axs[1].text(-0.2, 0.95, 'b', transform=axs[1].transAxes)
    axs[2].text(-0.2, 0.95, 'c', transform=axs[2].transAxes)
    axs[3].text(-0.2, 0.95, 'd', transform=axs[3].transAxes)
    axs[4].text(-0.2, 0.95, 'e', transform=axs[4].transAxes)
    axs[5].text(-0.2, 0.95, 'f', transform=axs[5].transAxes)
    plt.subplots_adjust(wspace=0.3, hspace=0.3)
    fig.savefig("fig2-modified", dpi=300)