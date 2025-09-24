import numpy as np
import mediapipe as mp
import cv2
import json
import os

mp_drawing = mp.solutions.drawing_utils # Drawing helpers
mp_pose = mp.solutions.pose # Pose estimation model

def get_pose_actions(landmarks):
    actions = {}
    LEFT_SHOULDER, RIGHT_SHOULDER = 11, 12
    LEFT_WRIST, RIGHT_WRIST = 15, 16
    LEFT_HIP, RIGHT_HIP = 23, 24
    LEFT_KNEE, RIGHT_KNEE = 25, 26

    def is_above(a, b):
        return landmarks[a]["y"] < landmarks[b]["y"]

    if landmarks[LEFT_WRIST]["visibility"] > 0.5:
        actions["left_arm"] = "raised" if is_above(LEFT_WRIST, LEFT_SHOULDER) else "down"
    if landmarks[RIGHT_WRIST]["visibility"] > 0.5:
        actions["right_arm"] = "raised" if is_above(RIGHT_WRIST, RIGHT_SHOULDER) else "down"
    if landmarks[LEFT_KNEE]["visibility"] > 0.5:
        actions["left_leg"] = "lifted" if is_above(LEFT_KNEE, LEFT_HIP) else "down"
    if landmarks[RIGHT_KNEE]["visibility"] > 0.5:
        actions["right_leg"] = "lifted" if is_above(RIGHT_KNEE, RIGHT_HIP) else "down"

    return actions

def analyze(video_path, output_path='outputs/poses_output.avi', json_path='outputs/poses_output.json'):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    os.makedirs(os.path.dirname(json_path), exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0 or np.isnan(fps):
        fps = 25

    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    all_landmarks = []
    frame_idx = 0

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                )

                landmarks = []
                for lm in results.pose_landmarks.landmark:
                    landmarks.append({
                        'x': float(lm.x),
                        'y': float(lm.y),
                        'z': float(lm.z),
                        'visibility': float(lm.visibility)
                    })

                pose_actions = get_pose_actions(landmarks)
                all_landmarks.append({
                    'frame': frame_idx,
                    'actions': pose_actions,
                    'landmarks': landmarks
                })

            out.write(image)
            frame_idx += 1

    # Pose summary
    pose_summary = {}
    for frame in all_landmarks:
        for part, state in frame["actions"].items():
            if part not in pose_summary:
                pose_summary[part] = {}
            if state not in pose_summary[part]:
                pose_summary[part][state] = 0
            pose_summary[part][state] += 1

    # Save JSON
    output = {"summary": pose_summary, "frames": all_landmarks}
    with open(json_path, 'w') as f:
        json.dump(output, f, indent=4)

    cap.release()
    out.release()

    print("Analysis complete.")
    print("Video saved to:", output_path)
    print("JSON saved to:", json_path)
