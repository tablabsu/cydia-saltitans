from matplotlib import pyplot as plt
import json, math

# Returns distance between points
def dist(x1, y1, x2, y2):
    return math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2))

set_prefix = "../experiments/"
sizes = [6.527, 6.722, 7.087, 7.162, 12.017, 12.372, 13.089, 13.483]
sets = [
    ["2021-07-14/video3/pos_data_1-4500.json", "2021-07-14/video3/pos_data_5000-9000.json"], 
    ["2021-07-15/video1/pos_data.json"], 
    ["2021-07-14/video1/pos_data.json"], 
    ["2021-07-15/video3/pos_data.json"], 
    ["2021-08-10/video4/pos_data_1-2200.json", "2021-08-10/video4/pos_data_2800-5600.json", "2021-08-10/video4/pos_data_5800-9000.json"], 
    ["2021-06-25/video2/pos_data_1-600.json", "2021-06-25/video2/pos_data_2200-2800.json", "2021-06-25/video2/pos_data_3200-3600.json"], 
    ["2021-08-16/video3/pos_data_1-2000.json", "2021-08-16/video3/pos_data_2200-7200.json"], 
    ["2021-08-16/video5/pos_data_1-4100.json", "2021-08-16/video5/pos_data_7500-9000.json"]
]

def get_delays(set_files):
    for f in set_files:
        objects = []
        canvas = {}
        with open(set_prefix + f) as fp:
            data = json.load(fp)
            objects = data['objects']
            canvas = data['canvas']
        fps = int(canvas['fps'])
        units = canvas['units']
        delays = []
        x = objects[0]['X']
        y = objects[0]['Y']
        d = 1
        for i in range(len(x) - 1):
            disp = dist(x[i], y[i], x[i+1], y[i+1])
            if disp < 0.1:
                d += 1
            else:
                if d >= fps:
                    delays.append(d)
                    d = 1
    return [int(d / fps) for d in delays]

def get_disps(set_files):
    for f in set_files:
        objects = []
        canvas = {}
        with open(set_prefix + f) as fp:
            data = json.load(fp)
            objects = data['objects']
            canvas = data['canvas']
        fps = int(canvas['fps'])
        disps = []
        x = objects[0]['X']
        y = objects[0]['Y']
        d = 1
        for i in range(len(x) - 1):
            disp = dist(x[i], y[i], x[i+1], y[i+1])
            if disp < 0.1:
                d += 1
            else:
                if d >= fps:
                    disps.append(disp)
                    d = 1
    return disps

with plt.style.context('science'):
    fig, axs = plt.subplots(4, 2, figsize=(3.5 * 2, 2.625 * 4))
    axs = axs.flatten()
    for i in range(len(axs)):
        delays = get_delays(sets[i])
        axs[i].set_title(f'Bean size: {sizes[i]}mm')
        axs[i].set_xlabel(r'$t_D$ (s)')
        axs[i].set_ylabel(r'P($t_D$)')
        axs[i].set_xlim(0, 25)
        axs[i].hist(delays, density=True, bins=max(delays), color=(0, 0, 0), histtype='step')
    plt.tight_layout()
    plt.show()
    if input("Save figure? ").lower() in ('y', 'yes'):
        print("Saving figure...")
        fig.savefig("supp-fig-delay", dpi=300)

with plt.style.context('science'):
    fig, axs = plt.subplots(4, 2, figsize=(3.5 * 2, 2.625 * 4))
    axs = axs.flatten()
    for i in range(len(axs)):
        disps = get_disps(sets[i])
        axs[i].set_title(f'Bean size: {sizes[i]}mm')
        axs[i].set_xlabel(r'$\delta$ (cm)')
        axs[i].set_ylabel(r'P($\delta$)')
        axs[i].set_xlim(0, 1.0)
        axs[i].hist(disps, density=True, bins=40, color=(0, 0, 0), histtype='step')
    plt.tight_layout()
    plt.show()
    if input("Save figure? ").lower() in ('y', 'yes'):
        print("Saving figure...")
        fig.savefig("supp-fig-disp", dpi=300)