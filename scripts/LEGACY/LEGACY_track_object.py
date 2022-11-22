from imutils.video import VideoStream
from imutils.video import FPS
import argparse
import imutils
import time
import logging
import cv2

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
logging.info("Logger initialized")

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str, help="path to input video file")
ap.add_argument("-t", "--tracker", type=str, default="mil", help="OpenCV object tracker type")
args = vars(ap.parse_args())
logging.info("Parsed command line args")

OPENCV_OBJECT_TRACKERS = {
    "mil": cv2.TrackerMIL_create,
    #"goturn": cv2.TrackerGOTURN_create, GOTURN requires an actual model file, tbd 
}

tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()
initBB = None

if not args.get("video", False):
    logging.info("Starting video stream")
    vs = VideoStream(src=0).start()
    #time.sleep(1.0)
else:
    logging.info("Capturing input video")
    vs = cv2.VideoCapture(args["video"])

cv2.namedWindow("Frame", cv2.WINDOW_NORMAL)
fps = None

while True:
    frame = vs.read()
    frame = frame[1] if args.get("video", False) else frame
    if frame is None:
        break

    frame = imutils.resize(frame, width=500)
    (H, W) = frame.shape[:2]

    if initBB is not None:
        (success, box) = tracker.update(frame)

        if success:
            (x, y, w, h) = [int(v) for v in box]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        fps.update()
        fps.stop()

        info = [
            ("Tracker", args["tracker"]),
            ("Success", "Yes" if success else "No"),
            ("FPS", "{:2f}".format(fps.fps())),
        ]

        for (i, (k, v)) in enumerate(info):
            text = "{}: {}".format(k, v)
            cv2.putText(frame, text, (10, H - ((i * 20) + 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
    cv2.imshow("Frame", frame)
    #cv2.resizeWindow('Frame', 1920, 1080) 
    key = cv2.waitKey(1) & 0xFF

    if key == ord("s"):
        logging.info("Initializing ROI")
        initBB = cv2.selectROI("Frame", frame, fromCenter=False, showCrosshair=True)
        tracker.init(frame, initBB)
        fps = FPS().start()
    elif key == ord("q"):
        break

if not args.get("video", False):
    vs.stop()
else:
    vs.release()
    
cv2.destroyAllWindows()


