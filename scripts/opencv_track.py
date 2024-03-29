import cv2
import numpy as np
import sys, os, argparse, logging, math, json, time

WINDOW = 'Contour and Centroid Calculation - OpenCV'
WINDOW_SIZE = (1300, 900)
TRACKBAR_NAME = "Frame"
FONT = cv2.FONT_HERSHEY_SIMPLEX 
CENTROID_MAX_RADIUS_PER = 0.05 # Percentage of width two centroids must be within to be combined
FOURCC = cv2.VideoWriter_fourcc(*'mp4v')

# --------- UTILITY METHODS --------- 

# Returns scalar distance between centroid positions
def centroid_dist(cp1, cp2):
    return math.sqrt(math.pow(cp1['X'] - cp2['X'], 2) + math.pow(cp1['Y'] - cp2['Y'], 2))

# Returns weighted centroid using area as weight of given centroids
def centroid_avg(cntrds):
    w_x = sum([i[0]['X']*i[1] for i in cntrds])
    w_y = sum([i[0]['Y']*i[1] for i in cntrds])
    areas = sum([i[1] for i in cntrds])
    if areas > 0:
        return ({'X': round(w_x / areas), 'Y': round(w_y / areas)}, areas)
    else:
        return ({'X': cntrds[0][0]['X'], 'Y': cntrds[0][0]['Y']}, 0)
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

# Converts units from pixels to given units
def convert_units(pix, pix_dim, real_dim):
    return round(pix * (real_dim/pix_dim), 3)

# -----------------------------------

# Setting up argument parser
parser = argparse.ArgumentParser(description="Multi-object tracking using OpenCV contour detection, centroid calculation, and tracking algorithms")
parser.add_argument("path", help="Path to video, ending in .avi or .mp4")
parser.add_argument("-rw", "--real-width", type=float, help="Real width of canvas, defaults to image height")
parser.add_argument("-rh", "--real-height", type=float, help="Real height of canvas, defaults to image height")
parser.add_argument("-u", "--units",  help="Units for canvas, defaults to 'pixels'")
parser.add_argument("-t", "--threshold", type=int, help="Image thresholding value, from 0 to 255, defaults to 128")
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

# Checking that given path points to an avi or mp4 file
if not os.path.split(args['path'])[-1].endswith(".avi") and not os.path.split(args['path'])[-1].endswith(".mp4"):
    logging.warning("Given path does not point to a .avi or .mp4 file! Exiting...")
    sys.exit(1)

pos_data = {"objects": [], "canvas": {}}
raw_data = []
times = []
est_total = 0
quit = False
vw = None
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
    
    # Start timer
    start = time.time()

    # Grab frame number and total frames
    frame_num = int(vs.get(cv2.CAP_PROP_POS_FRAMES))
    frame_total = int(vs.get(cv2.CAP_PROP_FRAME_COUNT))

    # Grab video frame dimensions, update canvas size
    height, width, _ = frame.shape
    if not pos_data['canvas']:
        pos_data['canvas']['width'] = args.get("real_width", width)
        pos_data['canvas']['height'] = args.get("real_height", height)
        pos_data['canvas']['units'] = args.get("units", "pixels")
        pos_data['canvas']['fps'] = int(vs.get(cv2.CAP_PROP_FPS))

    # Create VideoWriter if not created already
    if not vw:
        vw_fname = list(os.path.split(args['path']))
        vw_fname[-1] = "track-output.mp4"
        vw_fname = os.path.relpath(os.path.join(*vw_fname))
        vw = cv2.VideoWriter(vw_fname, FOURCC, int(frame_total / 60), (width, height))

    # Convert frame to gray colorspace
    framegray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Apply a threshold filter
    #ret, threshold = cv2.threshold(framegray, 128, 255, 0)
    #threshold = cv2.adaptiveThreshold(framegray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
    #ret, threshold = cv2.threshold(framegray, 128, 255, cv2.THRESH_TRUNC+cv2.THRESH_OTSU)
    ret, threshold = cv2.threshold(framegray, args.get("threshold", 128), 255, cv2.THRESH_BINARY)
    # Find and draw contours using cv2 simple chain approximation
    contours, hierarchy = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(frame, contours, -1, (0, 255, 0), 3)

    # DEBUG 
    #if frame_num == 1:
        #cv2.namedWindow("THRESHOLD DEBUG", cv2.WINDOW_NORMAL)
        #cv2.imshow("THRESHOLD DEBUG", threshold)

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
            cv2.putText(frame, "{0}\n{1}".format(c[1], (c[0]['X'], c[0]['Y'])), (c[0]['X'] + 25, c[0]['Y'] + 25), FONT, 0.5, (0, 0, 255), 2)
        
    # Removing first centroid, formed by borders of image
    centroids = centroids[1:]

    # Removing centroids over size threshold
    centroids = [c for c in centroids if c[1] < 1000000]

    # Removing centroids within 1% of border of image
    centroids = [c for c in centroids if not centroid_border(c, 0.05, frame.shape)]

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
        # Creating structure on first frame (converting units if necessary)
        raw_data = [{'X': [c['X']], 'Y': [c['Y']]} for c in centroids]
        pos_data['objects'] = [{'X': [convert_units(c['X'], width, args.get("real_width", width))], 'Y': [convert_units(c['Y'], height, args.get("real_height", height))]} for c in centroids]
    else:
        for c in centroids: 
            # Grabbing positions of all objects from last frame
            last_pos = [{'X': o['X'][-1], 'Y': o['Y'][-1]} for o in raw_data]
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
                #  Writing positions to position data (converting if necessary)
                raw_data[min_i]['X'].append(c['X'])
                raw_data[min_i]['Y'].append(c['Y'])
                pos_data["objects"][min_i]['X'].append(convert_units(c['X'], width, args.get("real_width", width)))
                pos_data["objects"][min_i]['Y'].append(convert_units(c['Y'], height, args.get("real_height", height)))
        # Fill in any failed tracks for an object with -1 x/y
        '''for obj in raw_data:
            if len(obj['X']) < frame_num:
                obj['X'].append(-1)
                obj['Y'].append(-1)'''

    # Draw resulting centroids
    for i in range(len(raw_data)):
        x = raw_data[i]['X'][-1]
        y = raw_data[i]['Y'][-1]
        cv2.circle(frame, (x, y), 5, (255, 0, 0), -1)
        cv2.putText(frame, "object {0}".format(i), (x - 50, y - 50), FONT, 1, (255, 0, 0), 2)

    # Label frame, write to video output
    cv2.putText(frame, "Frame {0} of {1}".format(frame_num, frame_total), (0, height - 10), FONT, 1, (0, 0, 255), 2)
    vw.write(frame)
    
    # Estimating time to process remaining frames
    end = time.time()
    times.append(end - start)
    elapsed = sum(times)
    est_total = (sum(times) / len(times)) * (frame_total - frame_num) + elapsed
    est_str = "{0}:{1} elapsed of {2}:{3}".format(str(math.floor(elapsed / 60)).zfill(2), str(math.floor(elapsed % 60)).zfill(2), str(math.floor(est_total / 60)).zfill(2), str(math.floor(est_total % 60)).zfill(2))
    cv2.putText(frame, est_str, (0, height - 50), FONT, 1, (0, 0, 255), 2)
    
    # Writing frame number
    cv2.putText(frame, "<Processing Mode>", (10, 30), FONT, 1, (0, 0, 0), 2)
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
logging.info("Releasing video read stream...")
vs.release()         
logging.info("Releasing video write stream...")
vw.release()
logging.info("Processing complete.")

logging.info("Position Data Info: ( objects: {0}, xlen: {1}, ylen: {2} )".format(len(pos_data['objects']), len(pos_data['objects'][0]['X']), len(pos_data['objects'][0]['Y'])))

# Saving position data to pos_data.json
pos_path = list(os.path.split(args['path']))
pos_path[-1] = 'pos_data.json'
pos_path = os.path.relpath(os.path.join(*pos_path))
logging.info("Saving position data to '{0}'...".format(pos_path))
with open(pos_path, "w+") as fp:
    json.dump(pos_data, fp)
logging.info("Position data saved.")
logging.info("Quitting...")

# Print bell character upon completion
print('\a')
cv2.destroyAllWindows()
