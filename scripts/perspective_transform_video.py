#! python3
import cv2
import numpy as np
import sys, os, argparse, logging, time, math

WINDOW = 'Perspective Transformation (video) - OpenCV'
WINDOW_SIZE = (1300, 900)
FONT = cv2.FONT_HERSHEY_SIMPLEX
FOURCC = cv2.VideoWriter_fourcc(*'mp4v')

# --------- UTILITY METHODS --------- 

# Callback method for cv2 mouse event
def click_points(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        if (len(params) < 4):
            # Skips if all four coordinates have been selected
            logging.debug("Clicked coordinates: {0}, {1}".format(x, y))
            cv2.putText(frame, str(x) + ',' + str(y), (x, y), FONT, 1, (255, 0, 0), 2)
            cv2.imshow(WINDOW, frame)
            params.append([x, y])
            logging.debug("Coordinate Array: {0}".format(params))
            if (len(params) == 4):
                # Called on last coordinate selection
                params = order_points(params, draw=True)
                shape_coords = np.array(params, np.int32).reshape((-1, 1, 2))
                cv2.polylines(frame, [shape_coords], True, (255, 0, 0), 2)
                cv2.imshow(WINDOW, frame)

# Returns distance between points
def dist(x1, y1, x2, y2):
    return math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2))

# Orders coordinate points to top left, bottom left, top right, bottom right
def order_points(coords, draw=False):
    sortx = sorted(coords)
    left = sortx[:2]
    right = sortx[2:]
    tl, bl = sorted(left, key=lambda k: [k[1], k[0]])
    tr, br = sorted(right, key=lambda k: [k[1], k[0]])
    if draw:
        return [tl, tr, br, bl]
    else:
        return [tl, bl, tr, br]

# -----------------------------------

# Setting up argument parser
parser = argparse.ArgumentParser(description="Perspective transform videos using OpenCV")
parser.add_argument("path", help="Path to video, ending in .mp4")
parser.add_argument("-d", "--debug", action="store_true", help="Show debug information")
args = vars(parser.parse_args())

# Setting up logger
format = "%(levelname)s : %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
logging.info("Retrieving video...")
if args.get("debug"):
    logging.getLogger().setLevel(logging.DEBUG)
logging.debug("ARGS: {0}".format(args))

# Check that path exists and ends in .mp4:
if not os.path.exists(args['path']):
    logging.warning("Given path does not exist! Exiting...")
    sys.exit(1)
if not os.path.split(args['path'])[-1].endswith('.mp4'):
    logging.warning("Given path does not point to a .mp4 file! Exiting...")
    sys.exit(1)

# Set up globals for processing loop
vs = cv2.VideoCapture(args['path'])
ret, frame = vs.read()
if not ret:
    logging.warning("Error occurred reading video file! Exiting...")
    sys.exit(1)
first_frame = frame.copy()
height, width, _ = frame.shape
frame_total = int(vs.get(cv2.CAP_PROP_FRAME_COUNT))
vs_fps = int(vs.get(cv2.CAP_PROP_FPS))
outname = list(os.path.split(args['path']))
outname[-1] = 'perspective-output.mp4'
outname = os.path.join(*outname)
vw = cv2.VideoWriter(outname, FOURCC, vs_fps, (width, height))
coords = []
quit = False
in_progress = True


# Create OpenCV window, register function to handle mouse clicks
cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW, WINDOW_SIZE[0], WINDOW_SIZE[1])
cv2.setMouseCallback(WINDOW, click_points, coords)

while in_progress:
    cv2.imshow(WINDOW, frame)
    # Wait for 'r', 'p', or 'q' key
    key = cv2.waitKey(1) & 0xFF
    if key == ord('r'):
        # Reset coordinates on R key
        coords.clear()
        height, width, _ = frame.shape
        frame = first_frame.copy()
        cv2.putText(frame, "ROI reset.", (0, height - 10), FONT, 1, (0, 0, 255), 2)
    elif key == ord('p'):
        # Process frames
        if len(coords) == 4:
            #frame = first_frame.copy()
            vs.set(cv2.CAP_PROP_POS_FRAMES, 0)
            times = []
            est_total = 0
            while True:
                
                # Read new frame
                ret, frame = vs.read()
                if not ret:
                    logging.info("Video stream ended...")
                    in_progress = False
                    break
                # Start timer
                start = time.time()

                # Grab frame number and frame dims
                frame_num = int(vs.get(cv2.CAP_PROP_POS_FRAMES))
                height, width, _ = frame.shape

                logging.info("Processing frame {0}...".format(frame_num))
                
                # Set up coords for transformation
                image_coords = np.float32([[0, 0], [0, height], [width, 0], [width, height]])
                transform_coords = np.float32(order_points(coords))

                # Create transform matrix and apply to image
                matrix = cv2.getPerspectiveTransform(transform_coords, image_coords)
                frame = cv2.warpPerspective(frame, matrix, (width, height))
                frame = cv2.resize(frame, (width, height))

                # Writing transformed image to videowriter stream
                vw.write(frame)

                # Displaying frame progress
                cv2.putText(frame, "Processing image {0} out of {1}".format(frame_num, frame_total), (0, height - 10), FONT, 1, (0, 0, 255), 2)

                # Est remaining time and showing on frame
                end = time.time()
                times.append(end - start)
                elapsed = sum(times)
                if (frame_num - 1) % 4 == 0:
                    est_total = (sum(times) / len(times)) * (frame_total - frame_num) + elapsed
                est_str = "{0}:{1} elapsed of {2}:{3}".format(str(math.floor(elapsed / 60)).zfill(2), str(math.floor(elapsed % 60)).zfill(2), str(math.floor(est_total / 60)).zfill(2), str(math.floor(est_total % 60)).zfill(2))
                cv2.putText(frame, est_str, (0, height - 50), FONT, 1, (0, 0, 255), 2)

                # Showing processed image
                cv2.imshow(WINDOW, frame)

                # Checking if user quitting
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    quit = True
                    break

    elif key == ord('q') or quit:
        # Quit program on Q key
        logging.info("Quitting...")
        break
# Print bell character upon completion
print('\a')
vs.release()
vw.release()
cv2.destroyAllWindows()
