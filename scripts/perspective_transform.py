#! python3
import cv2
import numpy as np
import sys, os, argparse, logging

IMAGE_ENDINGS = ("jpg", "bmp", "jpeg", "png")
IMAGE_PREFIX = "Image"
RESIZE_FACTOR = (8.5/11)
WINDOW = 'Perspective Transformation - OpenCV'
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

# Callback method for cv2 mouse event
def click_points(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        if (len(params) < 4):
            # Skips if all four coordinates have been selected
            logging.debug("Clicked coordinates: {0}, {1}".format(x, y))
            cv2.putText(image, str(x) + ',' + str(y), (x, y), FONT, 1, (255, 0, 0), 2)
            cv2.imshow(WINDOW, image)
            params.append([x, y])
            logging.debug("Coordinate Array: {0}".format(params))
            if (len(params) == 4):
                # Called on last coordinate selection
                shape_coords = np.array(params, np.int32).reshape((-1, 1, 2))
                cv2.polylines(image, [shape_coords], True, (255, 0, 0), 3)
                cv2.imshow(WINDOW, image)

# Orders coordinate points to top left, bottom left, top right, bottom right
def order_points(coords):
    output_coords = [[], [], [], []]
    # NOT IMPLEMENTED YET, CLICK IN RIGHT ORDER FOR NOW
    return coords

# -----------------------------------

# Setting up argument parser
parser = argparse.ArgumentParser(description="Perspective transform image sequences using OpenCV")
parser.add_argument("path", help="Path to folder with frames")
parser.add_argument("-d", "--debug", action="store_true", help="Show debug information")
args = vars(parser.parse_args())

# Setting up logger
format = "%(levelname)s : %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
logging.info("Searching for images...")
if args.get("debug"):
    logging.getLogger().setLevel(logging.DEBUG)
logging.debug("ARGS: {0}".format(args))
logging.debug("Resize factor: {0}".format(RESIZE_FACTOR))

# Checking that given path exists and is a folder
if not os.path.exists(args['path']) or not os.path.isdir(args['path']):
    logging.warning("Given path does not point to an existing folder! Exiting...")
    sys.exit(1)

# Ignore all files that are not images
im_files = os.listdir(args['path'])
logging.debug("Files in folder: {0}".format(", ".join(im_files)))
im_files = list(filter(lambda i : any([i.endswith(e) for e in IMAGE_ENDINGS]), im_files))
im_files.sort(key = lambda x : strip_frame_number(IMAGE_PREFIX, x))
logging.debug("Image files in folder: {0}".format(", ".join(im_files)))

# Checking that folder still contains image files after filtering
if len(im_files) == 0:
    logging.warning("No images found at given folder! Exiting...")
    sys.exit(1)

image = cv2.imread(os.path.join(args['path'], im_files[0]))
coords = []    

cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW, WINDOW_SIZE[0], WINDOW_SIZE[1])
cv2.setMouseCallback(WINDOW, click_points, coords)
while True:
    cv2.imshow(WINDOW, image)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("r"):
        # Reset coordinates on R key
        coords.clear()
        height, width, channels = image.shape
        image = cv2.imread(os.path.join(args['path'], im_files[0]))
        cv2.putText(image, "ROI reset.", (0, height - 10), FONT, 1, (0, 0, 255), 2)
    elif key == ord("p"):
        # Process rest of frames
        if len(coords) == 4:
            if not os.path.exists(os.path.join(args['path'], "transformed")):
                os.mkdir(os.path.join(args['path'], "transformed"))
            for (i, im) in enumerate(im_files):
                image = cv2.imread(os.path.join(args['path'], im))
                height, width, channels = image.shape
                image_coords = np.float32([[0, 0], [0, height], [width, 0], [width, height]])
                transform_coords = np.float32(order_points(coords))
                matrix = cv2.getPerspectiveTransform(transform_coords, image_coords)
                image = cv2.warpPerspective(image, matrix, (width, height))
                image = cv2.resize(image, (width, int(width*RESIZE_FACTOR)))
                cv2.imwrite(os.path.join(args['path'], "transformed", im), image)
                cv2.putText(image, "Processing image {0} out of {1}".format(i + 1, len(im_files)), (0, int(width*RESIZE_FACTOR) - 10), FONT, 1, (0, 0, 255), 2)
                cv2.imshow(WINDOW, image)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    logging.info("Stopping processing...")
                    coords.clear()
                    image = cv2.imread(os.path.join(args['path'], im_files[0]))
                    cv2.putText(image, "Processing stopped.", (0, height - 5), FONT, 1, (0, 0, 255), 2)
                    cv2.imshow(WINDOW, image)
                    break
            image = cv2.imread(os.path.join(args['path'], im_files[0]))
            cv2.putText(image, "Processing complete.", (0, height - 10), FONT, 1, (0, 0, 255), 2)
    elif key == ord("q"):
        # Quit program on Q key
        logging.info("Quitting...")
        break
cv2.destroyAllWindows()

