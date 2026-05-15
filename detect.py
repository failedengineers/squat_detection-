import cv2
import mediapipe as mp
import numpy as np


mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

pose = mp_pose.Pose(
    model_complexity=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Camera not working")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


counter = 0
stage = "UP"
angle_history = []

DOWN_THRESHOLD = 100
UP_THRESHOLD = 150

def calculate_angle(a, b, c):

    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = (
        np.arctan2(c[1] - b[1], c[0] - b[0])
        - np.arctan2(a[1] - b[1], a[0] - b[0])
    )

    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = 360 - angle

    return angle


while True:

    success, frame = cap.read()

    if not success:
        break

    # Mirror View
    frame = cv2.flip(frame, 1)

    # Convert BGR -> RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Pose Detection
    results = pose.process(rgb)

    form = "No Person"

    # =========================
    # Pose Found
    # =========================
    if results.pose_landmarks:

        mp_draw.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

        landmarks = results.pose_landmarks.landmark

        # LEFT SIDE
        hip = [
            landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
            landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y
        ]

        knee = [
            landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
            landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y
        ]

        ankle = [
            landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
            landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y
        ]

        # Calculate Angle
        angle = calculate_angle(hip, knee, ankle)

        # =========================
        # Smooth Angle
        # =========================
        angle_history.append(angle)

        if len(angle_history) > 5:
            angle_history.pop(0)

        smooth_angle = sum(angle_history) / len(angle_history)

        # =========================
        # Rep Counting Logic
        # =========================
        if smooth_angle < DOWN_THRESHOLD:
            stage = "DOWN"

        if smooth_angle > UP_THRESHOLD and stage == "DOWN":
            stage = "UP"
            counter += 1

        # =========================
        # Form Feedback
        # =========================
        if smooth_angle > 140:
            form = "Go Lower"

        elif 90 <= smooth_angle <= 140:
            form = "Perfect Squat"

        else:
            form = "Too Deep"

       
        cv2.putText(
            frame,
            f"Angle: {int(smooth_angle)}",
            (40, 220),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 255),
            3
        )

        cv2.putText(
            frame,
            f"Form: {form}",
            (40, 280),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 0),
            3
        )


    cv2.rectangle(frame, (0, 0), (420, 160), (30, 30, 30), -1)

    cv2.putText(
        frame,
        f"REPS: {counter}",
        (20, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.4,
        (0, 255, 0),
        3
    )

    
    cv2.putText(
        frame,
        f"STAGE: {stage}",
        (20, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        "Press Q to Quit",
        (20, 700),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (200, 200, 200),
        2
    )

    cv2.imshow("AI Squat Trainer", frame)


    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()