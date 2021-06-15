#! python3
import sys, os, argparse, logging
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation

# Setting up argument parser
parser = argparse.ArgumentParser(description="Display positions for .npz files in matplotlib plot")
parser.add_argument("path", help="Path to folder containing .npz files to be read")
parser.add_argument("-d", "--debug", action="store_true", help="Show debug information")
args = vars(parser.parse_args())

# Setting up logger
format = "%(levelname)s : %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
logging.info("Starting plotting...")
if args.get("debug"):
    logging.getLogger().setLevel(logging.DEBUG)
logging.debug("ARGS: {0}".format(args))

# Pull all files at given path
npz_paths = os.listdir(args["path"])
logging.debug("Files found: {0}".format(npz_paths))

# Filter files at path for .npz files
npz_paths = list(filter(lambda f: f.endswith(".npz"), npz_paths))
logging.debug("Filtered files (only .npz): {0}".format(npz_paths))

# Exit if there are no .npz files
if len(npz_paths) == 0:
    logging.warning("Failed to find any .npz files at the given path!")
    sys.exit(0)
else:
    logging.info("Found {0} .npz files.".format(len(npz_paths)))

frames = []

# Read position data, read x and y coords to each frame's 'x' and 'y' list
logging.info("Reading position data...")
for npz_file in npz_paths:
    path = os.path.join(args['path'], npz_file)
    with np.load(path) as npz:
        x = npz['X']
        y = npz['Y']
        for i in range(len(x)):
            if len(frames) <= i:
                frames.append({'x': [], 'y': []})
            frames[i]['x'].append(x[i])
            frames[i]['y'].append(y[i])

# Set up plots, set x and y lims (tentative)
logging.info("Setting up plots...")
fig, ax = plt.subplots()

# Flattening all x and y values across all frames, then calculating x and y limits
'''px = [i for l in [f['x'] for f in frames] for i in l if i != np.inf] 
py = [i for l in [f['y'] for f in frames] for i in l if i != np.inf]
logging.debug("PX: {0}, PY: {0}".format(px, py))
# Setting axis limits as [min(var) - stdev(var), max(var) + stdev(var)]
ax.set_xlim(min(px) - np.std(px), max(px) + np.std(px))
ax.set_ylim(min(py) - np.std(py), max(py) + np.std(py))'''
ax.set_xlim(0, 27.94)
ax.set_ylim(21.59, 0)
ax.set_xlabel('X position (cm)')
ax.set_ylabel('Y position (cm)')
ax.set_title('Jumping Bean Coordinates')
ax.xaxis.tick_top()

plot = plt.scatter([], [])

# Set up animation and updater function 
logging.info("Setting up animation...")
def update_anim(i):
    plot.set_offsets(np.array((i['x'], i['y'])).T)
    return plot
anim = animation.FuncAnimation(fig, update_anim, frames=frames)

plt.show()

# Ask user if they want to save animation, saves as containing folder's name and ".mp4"
if input("Save animation? ").lower() in ('y', 'yes'):
    anim_name = os.path.split(args['path'])[-1] + ".mp4"
    logging.info("Saving animation in '{0}' as '{1}'...".format(args['path'], anim_name))
    anim.save(os.path.join(args['path'], anim_name))
