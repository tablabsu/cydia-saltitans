#! python3
import sys, os, argparse, logging, json

# Setting up argument parser
parser = argparse.ArgumentParser(description="Append two position data files together")
parser.add_argument("file1", help="The first file to be appended")
parser.add_argument("file2", help="The second file to be appended")
parser.add_argument("-d", "--debug", action="store_true", help="Display debug information")
args = vars(parser.parse_args())

# Starting logger for status info
format = "%(levelname)s : %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S") 
logging.info("Trimming position data...")
if args.get("debug"):
    logging.getLogger().setLevel(logging.DEBUG)
logging.debug("ARGS: {0}".format(args)) # DEBUG

# Check that file1 path exists and ends in .json
if not os.path.exists(args['file1']):
    logging.warning("Given path for file1 does not exist! Exiting...")
    sys.exit(1)
if not os.path.split(args['file1'])[-1].endswith('.json'):
    logging.warning("Given path for file1 does not point to a .json file! Exiting...")
    sys.exit(1)

# Check that file2 path exists and ends in .json
if not os.path.exists(args['file2']):
    logging.warning("Given path for file2 does not exist! Exiting...")
    sys.exit(1)
if not os.path.split(args['file2'])[-1].endswith('.json'):
    logging.warning("Given path for file2 does not point to a .json file! Exiting...")
    sys.exit(1)

# Load position data from file1
file1_objects = []
file1_canvas = {}
with open(args['file1']) as fp:
    data = json.load(fp)
    file1_objects = data['objects']
    file1_canvas = data['canvas']

# Load position data from file2
file2_objects = []
file2_canvas = {}
with open(args['file2']) as fp:
    data = json.load(fp)
    file2_objects = data['objects']
    file2_canvas = data['canvas']

# Check that dimensions and units for both file are the same
if file1_canvas != file2_canvas:
    logging.warning("Given position files have different dimensions or units! Exiting...")
    sys.exit(1)

# Check that both position data files have the same number of objects
if len(file1_objects) != len(file2_objects):
    logging.warning("Given position data files have different number of objects! Exiting...")
    sys.exit(1)

# Append position data files together
appended_objects = []
for i in range(len(file1_objects)):
    new_obj = file1_objects[i]
    new_obj.extend(file2_objects[i])
    appended_objects.append(new_obj)

# Write appended position data to "pos_data_appended.json"
appended_pos_data = { 'canvas': file1_canvas, 'objects': appended_objects }
pos_path = list(os.path.split(args['file1']))
pos_path[-1] = "pos_data_appended.json"
pos_path = os.path.relpath(os.path.join(*pos_path))
with open(pos_path, 'w+') as fp:
    json.dump(appended_pos_data, fp)
logging.info("Saved appended position data to 'pos_data_appended.json'")
logging.info("Exiting...")