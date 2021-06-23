#! python3
import sys, os, argparse, logging, json
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation

# Setting up argument parser
parser = argparse.ArgumentParser(description="Display position from json position data files'")
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

# Read position data from file, move into correct format to display frames
frames = []
canvas = {}
with open(args['path']) as fp:
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

# Setting up plots
logging.info("Setting up plots...")
fig, ax = plt.subplots()
ax.set_xlim(0, canvas['width'])
ax.set_ylim(canvas['height'], 0) 
ax.set_xlabel("X position ({0})".format(canvas['units']))
ax.set_ylabel("Y position ({0})".format(canvas['units']))
ax.set_title("Jumping Bean Coordinates ({0})".format(canvas['units']))
ax.xaxis.tick_top()

plot = plt.scatter([], [])

# Set up animation and updater function
logging.info("Setting up animation...")
def update_anim(i):
    plot.set_offsets(np.array((i['X'], i['Y'])).T)
    ax.set_title("Jumping Bean Coordinates ({1}), Frame {0}".format(i["number"], canvas['units']))
    return plot
anim = animation.FuncAnimation(fig, update_anim, frames=frames)

plt.show()

# Ask user if they want to save animation
if input("Save animation? ").lower() in ('y', 'yes'):
    logging.info("Saving animation as animation.mp4...")
    writer = animation.FFMpegWriter(fps=1)
    anim.save("animation.mp4", writer=writer)