#! python3
import sys, os, argparse, logging

SETTINGS_PATH = os.path.abspath("../trex.settings")

# Setting up argument parser
parser = argparse.ArgumentParser(description="Run TRex with correct settings and paths")
parser.add_argument("path", help="Path to .pv file for TRex input")
parser.add_argument("-d", "--debug", action="store_true", help="Show debug information")
args = vars(parser.parse_args())

# Setting up logger
format = "%(levelname)s : %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
logging.info("Starting plotting...")
if args.get("debug"):
    logging.getLogger().setLevel(logging.DEBUG)
logging.debug("ARGS: {0}".format(args))

# Checking if given file ends in .pv
if not args["path"].lower().endswith(".pv"):
    logging.warning("Given path does not point to a .pv file! Exiting...")
    sys.exit(1)

# Checking if given file exists
if not os.path.exists(args['path']):
    logging.warning("Given path does not point to an existing file! Exiting...")
    sys.exit(1)

# Using absolute paths for arguments because TRex doesn't like relative paths
input_path = os.path.abspath(args['path'])
output_path = os.path.abspath(os.path.splitext(args['path'])[0])
logging.debug("INPUT PATH: {0}".format(input_path))
logging.debug("OUTPUT PATH: {0}".format(output_path))
logging.debug("SETTINGS PATH: {0}".format(SETTINGS_PATH))
os.system("trex -i {0} -output_dir {1} -s {2}".format(input_path, output_path, SETTINGS_PATH))
