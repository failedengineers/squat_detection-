AI Squat Counter

This project uses MediaPipe and OpenCV to detect human pose from a webcam and count squat repetitions in real time. It calculates the knee angle using hip, knee, and ankle points to determine squat movement.

The system tracks body movement continuously and counts a rep only when a full squat cycle is completed (standing → down → standing).

It helped in understanding real-time pose estimation, angle calculation, and movement tracking using computer vision.

How to run:
pip install opencv-python mediapipe numpy
python detect.py

Press Q to exit.
