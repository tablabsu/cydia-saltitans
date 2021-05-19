#! python3
import sys, os, argparse, logging
import imageio
import numpy as np
from skimage import io, filters, exposure

# Script constants here
EXPERIMENTS_PATH = os.path.join(os.pardir, "experiments")

# Setting up argument parser
parser = argparse.ArgumentParser(description="Preprocess videos for tracking using Fiji.")
parser.add_argument("experiment", help="Path to experiment in ../experiments, generally 'date/video'")
parser.add_argument("-ip", "--image-prefix", help="Prefix for video frame filename, defaults to 'Image'")
parser.add_argument("-nb", "--no-blur", action="store_true", help="Disable gaussian blur preprocessing")
parser.add_argument("-nc", "--no-contrast", action="store_true", help="Disable high contrast preprocessing")
parser.add_argument("-d", "--debug", action="store_true", help="Show debug information")
args = vars(parser.parse_args())


# Starting logger for status info
format = "%(levelname)s : %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S") 
logging.info("Starting preprocessing...")
if args.get("debug"):
    logging.getLogger().setLevel(logging.DEBUG)
logging.debug("ARGS: {0}".format(args)) # DEBUG

# Strips number from frame filename using image prefix and returns number of frame
def strip_frame_number(im_prefix, im_path):
    im_path = im_path.lstrip(im_prefix).split(".")[0]
    if im_path == "":
        return 0
    else:
        return int(im_path)


# Lists frames in order from frames folder
def list_frames(frames_path):
    # Loads image prefix from arguments, returns "Image" if not found
    im_prefix = args.get("image_prefix", "Image")
    
    # Lists files in frames folder, sorts by frame number in file name
    frames_list = os.listdir(frames_path)
    frames_list.sort(key = lambda x : strip_frame_number(im_prefix, x))

    logging.info("Found {0} frames".format(len(frames_list)))

    # Returns list of frames
    return frames_list

# Read frame files, apply preprocessing filters
def process_frames(frames, frames_path, video):
    im_prefix = args.get("image_prefix", "Image")
    for frame in frames:
        logging.info("Processing frame {0}".format(strip_frame_number(im_prefix, frame)))
        
        # Read frame file
        f = io.imread(os.path.join(frames_path, frame))

        # Apply gaussian blur
        if not args.get("no_blur"):
            f = filters.gaussian(f, 5)

        # Apply high contrast
        # TODO

        f = exposure.equalize_hist(f) # testing histogram equalization 

        # Write frame to video
        video.append_data(f)


if __name__ == "__main__":
    try:            
        v = imageio.get_writer(os.path.join(EXPERIMENTS_PATH, args["experiment"], "video.avi"), mode="I", fps=1)
        frames_path = os.path.join(EXPERIMENTS_PATH, args["experiment"], "frames")
        frames = list_frames(frames_path)
        process_frames(frames, frames_path, v)
        logging.info("Finalizing video...")
        v.close()
        logging.info("Preprocessing complete!")
    except KeyboardInterrupt:
        logging.warning("Interrupted! Exiting...")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)