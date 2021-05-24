import cv2
import numpy as np
import sys, os, argparse, logging

WINDOW = 'Contour and Centroid Calculation - OpenCV'
WINDOW_SIZE = (1500, 1100)
FONT = cv2.FONT_HERSHEY_SIMPLEX

# --------- UTILITY METHODS --------- 

# Returns number of frame, for sorting image files
def strip_frame_number(im_prefix, im_path):
    im_path = im_path.lstrip(im_prefix).split(".")[0]
    if im_path == "":
        return 0
    else:
        return int(im_path)

# Setting up argument parser
parser = argparse.ArgumentParser(description="Object tracking OpenCV contour detection, centroid calculation, and tracking algorithms")
parser.add_argument("path", help="Path to video, ending in .avi")
parser.add_argument("-d", "--debug", action="store_true", help="Show debug information")
args = vars(parser.parse_args())

# Setting up logger
format = "%(levelname)s : %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
logging.info("Loading video...")
if args.get("debug"):
    logging.getLogger().setLevel(logging.DEBUG)
logging.debug("ARGS: {0}".format(args))

# Checking that given path exists and is a folder
if not os.path.exists(args['path']):
    logging.warning("Given path does not exist! Exiting...")
    sys.exit(1)

# Checking that given path points to an avi file
if not os.path.split(args['path'])[-1].endswith(".avi"):
    logging.warning("Given path does not point to a .avi file! Exiting...")

vs = cv2.VideoCapture(args['path'])
cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW, WINDOW_SIZE[0], WINDOW_SIZE[1])
while True:
    # Read video frames
    ret, frame = vs.read()
    if not ret:
        logging.info("Video stream ended...")
        break

    # Grab video frame dimensions
    height, width, channels = frame.shape

    # Convert frame to gray colorspace
    framegray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Apply a threshold filter at 127 (middle gray)
    ret, threshold = cv2.threshold(framegray, 127, 255, 0)
    # Find and draw contours using cv2 simple chain approximation
    contours, hierarchy = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(frame, contours, -1, (0, 255, 0), 3)

    for (i, c) in enumerate(contours):
        M = cv2.moments(c)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else:
            cX, cY = 0, 0
        cv2.circle(frame, (cX, cY), 5, (255, 0, 0), -1)
        cv2.putText(frame, "centroid {0}".format(i), (cX - 25, cY - 25), FONT, 1, (255, 0, 0), 2)
    cv2.putText(frame, "Frame {0} of {1}".format(int(vs.get(cv2.CAP_PROP_POS_FRAMES)), int(vs.get(cv2.CAP_PROP_FRAME_COUNT))), (0, height - 5), FONT, 1, (0, 0, 255), 2)
    cv2.imshow(WINDOW, frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("p"):
        pass
    elif key == ord("q"):
        logging.info("Quitting...")
        break
vs.release()
cv2.destroyAllWindows()