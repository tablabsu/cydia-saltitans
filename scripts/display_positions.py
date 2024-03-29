#! python3
import sys, os, argparse, logging, json
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
from matplotlib import rcParams as rcp
from random import random
from random import uniform
import math
import pickle

# Setting up argument parser
parser = argparse.ArgumentParser(description="Display position from json position data files")
parser.add_argument("path", help="Path to file containing position data")
parser.add_argument("-c", "--cumulative", action="store_true", help="Show position line for all frames rather than ")
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
#rcp.update({'font.size': 20})
logging.info("Setting up plots...")
fig, ax = plt.subplots()
ax.set_xlim(0, canvas['width'])
ax.set_ylim(canvas['height'], 0) 
ax.set_xlabel("X position ({0})".format(canvas['units']))
ax.set_ylabel("Y position ({0})".format(canvas['units']))

if args.get("cumulative"):
    #color = (random(), random(), random())
    #color = (uniform(0.0, 0.5), uniform(0.0, 0.5), uniform(0.0, 0.5))
    color = (0, 0, 0)
    for i in range(len(frames) - 1):
        logging.info("Loading position frame {0}...".format(i))
        for o in range(len(frames[i]['X'])):
            plt.plot([frames[i]['X'][o], frames[i + 1]['X'][o]], [frames[i]['Y'][o], frames[i+1]['Y'][o]], color=color)

    # Move x and y limits
    logging.info("Calculating x and y limits...")
    x_pos = [f['X'][0] for f in frames]
    y_pos = [f['Y'][0] for f in frames]
    dist_pos = [math.sqrt(x_pos[i]**2 + y_pos[i]**2) for i in range(len(x_pos))]
    dist_stdev = np.std(dist_pos) * 2
    ax.set_xlim(min(x_pos) - dist_stdev, max(x_pos) + dist_stdev)
    ax.set_ylim(max(y_pos) + dist_stdev, min(y_pos) - dist_stdev)
    #ax.set_xlim(0, 27.94)
    #ax.set_ylim(21.59, 0)

    # Displaying plot
    logging.info("Showing plot...")
    plt.show()

    # Ask user if they want to save figure
    if input("Save figure? ").lower() in ('y', 'yes'):
        logging.info("Saving figure...")
        fig.savefig("figure-positions")
        fig.savefig('figure-positions.svg', format='svg')
else:
    # Set up animation and updater function
    plot = plt.scatter([], [])
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
