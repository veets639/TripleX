import os

import cv2


def extract_sharpest_frame(video_path):
    cap = cv2.VideoCapture(video_path)
    max_var = 0
    sharpest_frame = None
    frame_number = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        if variance > max_var:
            max_var = variance
            sharpest_frame = frame.copy()
            best_frame_number = frame_number
        frame_number += 1

    cap.release()
    if sharpest_frame is not None:
        output_dir = os.path.join('data', 'images')
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        frame_filename = f"{base_name}_frame_{best_frame_number}.jpg"
        frame_path = os.path.join(output_dir, frame_filename)
        cv2.imwrite(frame_path, sharpest_frame)
        return frame_path
    else:
        return None
