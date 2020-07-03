# Baby-Eye-Tracker
A CNN that classifies discrete eye gaze direction ("Left", "Right", "Away") from children videos.
Based on "Automatic, Real-Time Coding of Looking-While-Listening Children Videos Using Neural Networks" presented in [ICIS 2020](https://infantstudies.org/congress-2020).


# Step 1:
Install requirements (python >= 3.6):

`pip install -r requirements.txt`

# Step 2:
Download the latest network model & weights file [here](https://www.cs.tau.ac.il/~yotamerel/baby_eye_tracker/model.h5).
This is a keras model h5 file which contains both the architecture and the weights.

Download the face extraction model files (opencv dnn):

[prototxt (contains architecture)](https://www.cs.tau.ac.il/~yotamerel/baby_eye_tracker/config.prototxt)

[caffemodel (contains weights)](https://www.cs.tau.ac.il/~yotamerel/baby_eye_tracker/face_model.caffemodel)

Put files in the same directory as "example.py".

# Step 3:
Run the example file with the webcam:

`python example.py --webcam mywebcam_id`

Run the example file with a video file:

`python example.py --video_file /path/to/my/video.avi`
