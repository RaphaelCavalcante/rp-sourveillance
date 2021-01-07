from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
import threading
import argparse
import datetime
import imutils
import time
import cv2

outputFrame = None
lock = threading.Lock()
app=Flask(__name__)
stream = VideoStream(src=0).start()

@app.route("/")
def index():
    return render_template("./index.html")

@app.route("/video_feed")
def video_feed():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")
def read_cam(arg):
    global vs, outputFrame, lock
    while True:
        frame = stream.read()
        frame = imutils.resize(frame, width=400)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)

        # with lock:
        outputFrame = frame.copy()

def generate():
    global outputFrame, lock
    while True:
        # with lock:
        if outputFrame is None:
            continue
        (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
        if not flag:
            continue
        yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n'+ bytearray(encodedImage) +b'\r\n')

if __name__ == '__main__':
	# construct the argument parser and parse command line arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--ip", type=str, required=True,
		help="ip address of the device")
	ap.add_argument("-o", "--port", type=int, required=True,
		help="ephemeral port number of the server (1024 to 65535)")
	ap.add_argument("-f", "--frame-count", type=int, default=32,
		help="# of frames used to construct the background model")
	args = vars(ap.parse_args())
	# start a thread that will perform motion detection
	t = threading.Thread(target=read_cam, args=(
		args["frame_count"],))
	t.daemon = True
	t.start()
	# start the flask app
	app.run(host=args["ip"], port=args["port"], debug=True,
		threaded=True, use_reloader=False)
# release the video stream pointer
stream.stop()