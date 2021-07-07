#! python3
import sys, os, argparse, logging, time, math
import cv2

WINDOW = 'Preprocessing (Video) - OpenCV'
WINDOW_SIZE = (1500, 1100)
FONT = cv2.FONT_HERSHEY_SIMPLEX
FOURCC = cv2.VideoWriter_fourcc(*'mp4v')

# Setting up argument parser
parser = argparse.ArgumentParser(description="Preprocess videos for tracking using OpenCV to filter frames.")
parser.add_argument("path", help="Path to video, ending in .mp4")
parser.add_argument("-d", "--debug", action="store_true", help="Show debug information")
args = vars(parser.parse_args())

# Starting logger for status info
format = "%(levelname)s : %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S") 
logging.info("Starting preprocessing...")
if args.get("debug"):
    logging.getLogger().setLevel(logging.DEBUG)
logging.debug("ARGS: {0}".format(args)) # DEBUG

# Check that path exists and ends in .mp4
if not os.path.exists(args['path']):
    logging.warning("Given path does not exist! Exiting...")
    sys.exit(1)
if not os.path.split(args['path'])[-1].endswith('.mp4'):
    logging.warning("Given pat hdoes not point to a .mp4 file! Exiting...")
    sys.exit(1)

# Setting up video objects
vs = cv2.VideoCapture(args['path'])
ret, frame = vs.read()
if not ret:
    logging.warning("Error occurred reading video file! Exiting...")
    sys.exit(1)
height, width, _ = frame.shape
frame_total = int(vs.get(cv2.CAP_PROP_FRAME_COUNT))
vs_fps = int(vs.get(cv2.CAP_PROP_FPS))
outname = list(os.path.split(args['path']))
outname[-1] = 'preprocessed-output.mp4'
outname = os.path.join(*outname)
vw = cv2.VideoWriter(outname, FOURCC, vs_fps, (width, height))

# Create OpenCV window
cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW, WINDOW_SIZE[0], WINDOW_SIZE[1])

times = []
est_total = 0
while True:
    # Start timer
    start = time.time()

    # Grab current frame number
    frame_num = int(vs.get(cv2.CAP_PROP_POS_FRAMES))
    
    # Process frame
    frame = cv2.GaussianBlur(frame, (5, 5), 0)
    frame = cv2.addWeighted(frame, 1.6, frame, 0, 0)
    #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #frame = cv2.equalizeHist(frame)
    #frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

    # Write frame to VideoWriter
    vw.write(frame)
    
    # Write processing progress to frame
    cv2.putText(frame, "Processing image {0} out of {1}".format(frame_num, frame_total), (0, height - 10), FONT, 1, (0, 0, 255), 2)
    
    # Estimate time left and write to frame
    end = time.time()
    times.append(end - start)
    elapsed = sum(times)
    if (frame_num - 1) % 4 == 0:
        est_total = (sum(times) / len(times)) * (frame_total - frame_num) + elapsed
    est_str = "{0}:{1} elapsed of {2}:{3}".format(str(math.floor(elapsed / 60)).zfill(2), str(math.floor(elapsed % 60)).zfill(2), str(math.floor(est_total / 60)).zfill(2), str(math.floor(est_total % 60)).zfill(2))
    cv2.putText(frame, est_str, (0, height - 50), FONT, 1, (0, 0, 255), 2)

    # Show frame
    cv2.imshow(WINDOW, frame)

    # Check if user trying to quit
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        logging.info("Quitting...")
        break

    # Read next frame, otherwise end if video stops reading frames
    ret, frame = vs.read()
    if not ret:
        logging.info("Video stream ended...")
        break
vs.release()
vw.release()
cv2.destroyAllWindows()