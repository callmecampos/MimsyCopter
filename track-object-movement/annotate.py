from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time

# python object_movement.py --video object_tracking_example.mp4

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
args = vars(ap.parse_args())

# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
refPt, count = (-1, -1), 0

def click_and_crop(event, x, y, flags, param):
    # grab references to the global variables
    global refPt, count

    # check to see if the left mouse button was released
    if event == cv2.EVENT_LBUTTONUP:
    	# record the ending (x, y) coordinates
        refPt = (x, y)
        count += 1

vs = cv2.VideoCapture(args["video"])
fps = vs.get(cv2.CAP_PROP_FPS)

j = 0
frames = []
while True:
    # grab the current frame
    frame = vs.read()

    # handle the frame from VideoCapture or VideoStream
    frame = frame[1] if args.get("video", False) else frame

    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if frame is None:
        break

    frames.append(frame)

    j+=1
    print(j, end='\r')

locations, i, new, last_id = [], -1, True, count
frame_count = 0
id = 0
while id < len(frames):
    frame = frames[id]

    frame_count += 1
    cv2.putText(frame, "Time: {}".format(frame_count / fps),
		(10, 30), cv2.FONT_HERSHEY_SIMPLEX,
		0.5, (0, 255, 0), 1)

    cv2.imshow("Frame", frame)
    cv2.setMouseCallback("Frame", click_and_crop)

    key = cv2.waitKey(20*1000) & 0xFF

    if new:
        new = False
        locations.append([])
        i += 1

    if key == ord("c"): # continue
        continue
    elif key == ord("b"): # back
        id -= 1
    elif key == ord("n"): # new pose
        new = True
        print("New pose.")
    elif key == ord("s"): # save the annotated point
        if count > last_id:
            last_id = count
            locations[i].append(refPt)
        else:
            print("You did not annotate a point.")
    elif key == ord("p"):
        print(locations)
    elif key == ord("q"): # quit
        print("DIMENSIONS: {}".format(frame.shape[:2]))
        break

    id += 1

print("\n\nDUMP:\n")
print(locations)

vs.release()

# close all windows
cv2.destroyAllWindows()
