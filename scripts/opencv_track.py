import cv2
import numpy as np
import sys, os, argparse, logging, math

WINDOW = 'Contour and Centroid Calculation - OpenCV'
WINDOW_SIZE = (1500, 1100)
FONT = cv2.FONT_HERSHEY_SIMPLEX 
CENTROID_MAX_RADIUS_PER = 0.05 # Percentage of width two centroids must be within to be combined

# --------- UTILITY METHODS --------- 

# Returns number of frame, for sorting image files
def strip_frame_number(im_prefix, im_path):
    im_path = im_path.lstrip(im_prefix).split(".")[0]
    if im_path == "":
        return 0
    else:
        return int(im_path)

# Returns scalar distance between centroid positions
def centroid_dist(cp1, cp2):
    return math.sqrt(math.pow(cp1['X'] - cp2['X'], 2) + math.pow(cp1['Y'] - cp2['Y'], 2))

# Returns weighted centroid using area as weight of given centroids
def centroid_avg(cntrds):
    w_x = sum([i[0]['X']*i[1] for i in cntrds])
    w_y = sum([i[0]['Y']*i[1] for i in cntrds])
    areas = sum([i[1] for i in cntrds])
    return ({'X': round(w_x / areas), 'Y': round(w_y / areas)}, areas)

# Returns true if c is within factor percent of image borders
def centroid_border(c, factor, shape):
    height, width, channels = shape
    if c[0]['X'] <= factor*width or c[0]['X'] >= (1 - factor)*width:
        return True
    elif c[0]['Y'] <= factor*height or c[0]['X'] >= (1 - factor)*height:
        return True
    return False

# Setting up argument parser
parser = argparse.ArgumentParser(description="Object tracking OpenCV contour detection, centroid calculation, and tracking algorithms")
parser.add_argument("path", help="Path to video, ending in .avi")
parser.add_argument("-d", "--debug", action="store_true", help="Show debug information")
parser.add_argument("--debug-disable-avg", action="store_true", help="DEBUG: Disable averaging nearby centroids")
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

kill = 0
vs = cv2.VideoCapture(args['path'])
quit = False
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
    contours, hierarchy = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(frame, contours, -1, (0, 255, 0), 3)

    # Calculate centroids
    centroids = []
    for (i, c) in enumerate(contours):
        M = cv2.moments(c)
        if M["m00"] != 0: # Ignores erroring centroids, potentially worth tracking those
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            centroids.append(({'X': cX, 'Y': cY}, int(M['m00'])))

    # Removing first centroid, formed by borders of image
    centroids = centroids[1:]

    # Removing centroids within 1% of border of image
    centroids = [c for c in centroids if not centroid_border(c, 0.01, frame.shape)]
        
    # Pass over centroids, combine those within set radius into their weighted average centroid
    if not args.get("debug_disable_avg"):
        filtered_centroids = []
        centr = centroids
        while len(centr) > 0:
            near = [centr[0]] + [i for i in centr if centroid_dist(centr[0][0], i[0]) <= (CENTROID_MAX_RADIUS_PER * width)]
            centr = [i for i in centr if centroid_dist(centr[0][0], i[0]) > (CENTROID_MAX_RADIUS_PER * width)]
            filtered_centroids.append(centroid_avg(near))
    else:
        filtered_centroids = centroids

    if args.get("debug"):
        logging.debug("FRAME {0} CENTROIDS: {1}".format(int(vs.get(cv2.CAP_PROP_FRAME_COUNT)), centroids))
        logging.debug("FRAME {0} FILTERED CENTROIDS: {1}".format(int(vs.get(cv2.CAP_PROP_FRAME_COUNT)), filtered_centroids))
        for (c, _) in centroids:
            cv2.circle(frame, (c['X'], c['Y']), 5, (0, 255, 255), -1)

    # Removing area data for drawing
    centroids = [c for (c, a) in filtered_centroids] 

    # Draw resulting centroids
    for (i, c) in enumerate(centroids):
        cv2.circle(frame, (c['X'], c['Y']), 5, (255, 0, 0), -1)
        cv2.putText(frame, "centroid {0}".format(i), (c['X'] - 25, c['Y'] - 25), FONT, 1, (255, 0, 0), 2)
    
    # Writing frame number
    cv2.putText(frame, "Frame {0} of {1}".format(int(vs.get(cv2.CAP_PROP_POS_FRAMES)), int(vs.get(cv2.CAP_PROP_FRAME_COUNT))), (0, height - 10), FONT, 1, (0, 0, 255), 2)
    cv2.imshow(WINDOW, frame)

    key = cv2.waitKey(1) & 0xFF

    # Pause processing with p
    if key == ord("p"):
        key = cv2.waitKey(1) & 0xFF
        # Wait for p to play again
        while key != ord("p"):
            # Quit while paused
            if key == ord("q"):
                quit = True
                break
            key = cv2.waitKey(1) & 0xFF
    elif key == ord("q") or quit:
        logging.info("Quitting...")
        break
vs.release()
cv2.destroyAllWindows()