#! python3
import sys, os, argparse, logging, json

# Setting up argument parser
parser = argparse.ArgumentParser(description="Trim position data from file, seeking to specific frame")
parser.add_argument("path", help="Path to position data file")
parser.add_argument("-ss", "--seek", type=int, help="Seek to specific frame in position data file")
parser.add_argument("-to", "--to", type=int, help="Retrieve position data until specific frame")
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

# Set up seek and to 
seek = args['seek']
if not seek:
    seek = 1
to = args['to']
if not to:
    to = len(objects[0]['X'])

# Check seek and to are correct
if seek > to:
    logging.warning("Seek should be before to! Exiting...")
    sys.exit(1)
if seek > len(objects[0]['X']) or to > len(objects[0]['X']):
    logging.warning("Seek or to is too far! Exiting...")
    sys.exit(1)
if seek < 1 or to < 1:
    logging.warning("Seek and to must begin at frame 1! Exiting...")
    sys.exit(1)

# Trim position data
trimmed_objs = []
for obj in objects:
    x = obj['X'][seek-1:to-1]
    y = obj['Y'][seek-1:to-1]
    trimmed_objs.append({ 'X': x, 'Y': y })
objects = trimmed_objs

# Reassemble position data file and save to pos_data_XX-XX.json
pos_data = { 'objects': objects, 'canvas': canvas }
pos_path = list(os.path.split(args['path']))
pos_path[-1] = "pos_data_{0}-{1}.json".format(seek, to)
pos_path = os.path.relpath(os.path.join(*pos_path))
with open(pos_path, "w+") as fp:
    json.dump(pos_data, fp)
logging.info("Saved trimmed position data to 'pos_data_{0}-{1}.json'.".format(seek, to))
logging.info("Exiting...")