#! python3
import sys, os, argparse, logging, time, math
import numpy as np
import cv2

# Script constants here
IMAGE_PREFIX = "Image"

# Setting up argument parser
parser = argparse.ArgumentParser(description="Preprocess videos for tracking using OpenCV to modify frames and stitch into video.")
parser.add_argument("path", help="Path to image frames")
parser.add_argument("-nfx", "--nofx", action="store_true", help="Disable filtering video, just dump raw frames")
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
    # Lists files in frames folder, sorts by frame number in file name
    frames_list = os.listdir(frames_path)
    frames_list = list(filter(lambda f: f.endswith(".jpg") or f.endswith(".png"), frames_list))
    frames_list.sort(key = lambda x : strip_frame_number(IMAGE_PREFIX, x))

    logging.info("Found {0} frames".format(len(frames_list)))

    # Returns list of frames
    return frames_list

# Read frame files, apply preprocessing filters
def process_frames(frames, frames_path, video):
    times = []
    est_total = 0
    for i, frame in enumerate(frames):
        start = time.time()
        logging.info("Processing frame {0}".format(strip_frame_number(IMAGE_PREFIX, frame)))

        # Read frame file
        f = cv2.imread(os.path.join(frames_path, frame))

        if not args.get("nofx"):
            # Apply gaussian blur
            #f = filters.gaussian(f, 5)

            # Apply high contrast
            f = cv2.addWeighted(f, 1.6, f, 0, 0)
            
            # Convert to grayscale (for histogram eq.)
            #f = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)

            # Apply histogram equalization
            #f = cv2.equalizeHist(f) 
            #clahe = cv2.createCLAHE()
            #f = clahe.apply(f)
            #_, f = cv2.threshold(f, 160, 255, cv2.THRESH_BINARY)

            # Convert back to BGR for video writing
            #f = cv2.cvtColor(f, cv2.COLOR_GRAY2BGR)

        # Write frame to video
        video.write(f)

        end = time.time()
        times.append(end - start)
        elapsed = sum(times)
        if i % 4 == 0:
            est_total = (sum(times) / len(times)) * (len(frames) - i) + elapsed
        logging.info("Frame took {0} seconds to process, approx. {1}:{2} remaining.".format(round(end - start, 2), str(math.floor(est_total / 60)).zfill(2), str(math.floor(est_total % 60)).zfill(2)))

if __name__ == "__main__":
    try:            
        #v = imageio.get_writer(os.path.join(args["path"], "video.avi"), mode="I", fps=1)
        frames_path = os.path.join(args["path"])
        frames = list_frames(frames_path)
        height, width, _ = cv2.imread(os.path.join(args['path'], frames[0])).shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        v_name = "video.mp4"
        if args.get("nofx"):
            v_name = "video-nofx.mp4"
        v = cv2.VideoWriter(os.path.join(args['path'], v_name), fourcc, 1, (width, height))
        process_frames(frames, frames_path, v)
        logging.info("Finalizing video...")
        cv2.destroyAllWindows()
        v.release()
        logging.info("Preprocessing complete!")
    except KeyboardInterrupt:
        logging.warning("Interrupted! Exiting...")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)