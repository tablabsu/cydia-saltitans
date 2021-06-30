#! python3
import sys, os, argparse, logging, json

# Setting up argument parser
parser = argparse.ArgumentParser(description="")
parser.add_argument("path", help="Path to position data file")
parser.add_argument("-o", "--objects", required=True, help="Index of objects to calculate delays for, accepts comma-separated list of indices")
parser.add_argument("-d", "--debug", action="store_true", help="Show debug information")
args = vars(parser.parse_args())

# Starting logger for status info
format = "%(levelname)s : %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S") 
logging.info("Trimming position data...")
if args.get("debug"):
    logging.getLogger().setLevel(logging.DEBUG)
logging.debug("ARGS: {0}".format(args)) # DEBUG

# Check that file at path exists and ends in .json
if not os.path.exists(args["path"]):
    logging.warning("Given path does not exist! Exiting...")
    sys.exit(1)
if not os.path.split(args["path"])[-1].endswith(".json"):
    logging.warning("Given path does not point to a .json file! Exiting...")
    sys.exit(1)

# Load position data from file
objects = []
canvas = {}
with open(args['path']) as fp:
    data = json.load(fp)
    objects = data['objects']
    canvas = data['canvas']

# Select only objects
obj_i = [int(i) for i in args['objects'].split(",")]
obj_i.sort()
selected_objects = []
for o in obj_i:
    selected_objects.append(objects[o])

# Saves to same path as given, overwriting initial file
pos_data = { 'objects': selected_objects, 'canvas': canvas }
with open(args['path'], 'w+') as fp:
    json.dump(pos_data, fp)
logging.info("Saved position data with selected objects to '{0}'.".format(list(os.path.split(args['path']))[-1]))
logging.info("Exiting...")