import cv2
import numpy as np
import sys, os, argparse, logging, math, json

WINDOW = 'Contour and Centroid Calculation - OpenCV'
WINDOW_SIZE = (1500, 1100)
TRACKBAR_NAME = "Frame"
FONT = cv2.FONT_HERSHEY_SIMPLEX 
CENTROID_MAX_RADIUS_PER = 0.05 # Percentage of width two centroids must be within to be combined

# --------- UTILITY METHODS --------- 

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
    height, width, _ = shape
    if c[0]['X'] <= factor*width or c[0]['X'] >= (1 - factor)*width:
        return True
    elif c[0]['Y'] <= factor*height or c[0]['Y'] >= (1 - factor)*height:
        return True
    return False

# Kills execution with error message, closes video handle and cv2 windows
def kill_execution(errormsg, videohandle=None, spin=True):
    logging.warning(errormsg)
    if spin:
        key = cv2.waitKey(1) & 0xFF
        while key != ord("q"):
            key = cv2.waitKey(1) & 0xFF
    logging.info("Quitting...")
    if videohandle:
        videohandle.release()
    cv2.destroyAllWindows()
    sys.exit(1)

# Function passed to frame trackbar
def trackbar_update(val):
    global current_frame
    current_frame = val
    cv2.imshow(WINDOW, drawn_frames[current_frame])

# -----------------------------------

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

pos_data = {"objects": []}
drawn_frames = []
quit = False
vs = cv2.VideoCapture(args['path'])
cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW, WINDOW_SIZE[0], WINDOW_SIZE[1])
key = cv2.waitKey(1) & 0xFF
while True:
    # Read video frames
    ret, frame = vs.read()
    if not ret:
        logging.info("Video stream ended...")
        break

    # Grab frame number and total frames
    frame_num = int(vs.get(cv2.CAP_PROP_POS_FRAMES))
    frame_total = int(vs.get(cv2.CAP_PROP_FRAME_COUNT))

    # Grab video frame dimensions
    height, width, _ = frame.shape

    # Convert frame to gray colorspace
    framegray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Apply a threshold filter
    ret, threshold = cv2.threshold(framegray, 200, 255, 0)
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

    # Drawing deleted points, ranges, and size/coords if debug is on
    if args.get("debug"):
        for c in centroids:
            cv2.circle(frame, (c[0]['X'], c[0]['Y']), 5, (0, 0, 255), -1)
            cv2.circle(frame, (c[0]['X'], c[0]['Y']), int(CENTROID_MAX_RADIUS_PER * width), (0, 255, 255), 2)
            cv2.putText(frame, "{0}\n{1}".format(c[1], (c[0]['X'], c[0]['Y'])), (c[0]['X'] + 25, c[0]['Y'] + 25), FONT, 1, (0, 0, 255), 2)
        
    # Removing first centroid, formed by borders of image
    centroids = centroids[1:]

    # Removing centroids within 1% of border of image
    centroids = [c for c in centroids if not centroid_border(c, 0.01, frame.shape)]

    # Pass over centroids, combine those within set radius into their weighted average centroid
    filtered_centroids = []
    while len(centroids) > 0:
        # Average together all points within radius of selected point, update centroid list to all points not near selected point
        near = [centroids[0]] + [i for i in centroids[1:] if centroid_dist(centroids[0][0], i[0]) <= (CENTROID_MAX_RADIUS_PER * width)]
        centroids = [i for i in centroids[1:] if centroid_dist(centroids[0][0], i[0]) > (CENTROID_MAX_RADIUS_PER * width)]
        filtered_centroids.append(centroid_avg(near))

    # Removing area data from centroids
    centroids = [c for (c, a) in filtered_centroids] 

    if frame_num == 1:
        [pos_data["objects"].append({'X': [c['X']], 'Y': [c['Y']]}) for (i, c) in enumerate(centroids)]
    else:
        for c in centroids: 
            # Grabbing positions of all objects from last frame
            last_pos = [{'X': o['X'][-1], 'Y': o['Y'][-1]} for o in pos_data['objects']]
            
            # Find last frame object closest to current point
            min_i = -1
            min_dist = max([height, width]) + 1
            for (i, pos) in enumerate(last_pos):
                if centroid_dist(c, pos) < min_dist:
                    min_i = i
                    min_dist = centroid_dist(c, pos)
            if min_i == -1:
                kill_execution("Error: Could not match centroid to object!", vs)
            else:
                pos_data["objects"][min_i]['X'].append(c['X'])
                pos_data["objects"][min_i]['Y'].append(c['Y'])

    # Draw resulting centroids
    for (i, _) in enumerate(centroids):
        x = pos_data["objects"][i]['X'][-1]
        y = pos_data["objects"][i]['Y'][-1]
        cv2.circle(frame, (x, y), 5, (255, 0, 0), -1)
        cv2.putText(frame, "object {0}".format(i), (x - 50, y - 50), FONT, 1, (255, 0, 0), 2)

    cp_frame = frame.copy()
    cv2.putText(cp_frame, "Frame {0} of {1}".format(frame_num, frame_total), (0, height - 10), FONT, 1, (0, 0, 255), 2)
    cv2.putText(cp_frame, "<Playback Mode>", (10, 30), FONT, 1, (0, 0, 0), 2)
    drawn_frames.append(cp_frame)
    
    # Writing frame number
    cv2.putText(frame, "<Processing Mode>", (10, 30), FONT, 1, (0, 0, 0), 2)
    cv2.putText(frame, "Processing frame {0} of {1}".format(frame_num, frame_total), (0, height - 10), FONT, 1, (0, 0, 255), 2)
    cv2.imshow(WINDOW, frame)

    # Checking if a key was pressed
    key = cv2.waitKey(1) & 0xFF
    if key == ord("p"):
        # Pause on p and wait for key press
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
        vs.release()
        cv2.destroyAllWindows()
        sys.exit(0)
logging.info("Releasing video stream...")
vs.release()         
logging.info("Processing complete.")

pos_path = list(os.path.split(args['path']))
pos_path[-1] = 'pos_data.json'
pos_path = os.path.relpath(os.path.join(*pos_path))
logging.info("Saving position data to '{0}'...".format(pos_path))
with open(pos_path, "w+") as fp:
    json.dump(pos_data, fp)
logging.info("Position data saved.")

# Beginning playback
logging.info("Beginning playback...")
current_frame = 1
paused = True
cv2.createTrackbar(TRACKBAR_NAME, WINDOW, 0, len(drawn_frames) - 1, trackbar_update)
cv2.imshow(WINDOW, drawn_frames[0])
while True:
    key = cv2.waitKey(1) & 0xFF
    if key == ord("p"):
        paused = True
    if paused:
        key = cv2.waitKey(1) & 0xFF
        while key != ord("p"):
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                quit = True
                break
        paused = False
    if key == ord("q") or quit:
        break
    current_frame += 1
    if current_frame >= len(drawn_frames):
        current_frame = 1
    cv2.setTrackbarPos(TRACKBAR_NAME, WINDOW, current_frame)
logging.info("Ending playback.")
logging.info("Quitting...")
cv2.destroyAllWindows()