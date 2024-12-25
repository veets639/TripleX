import argparse

import cv2
import numpy as np
import os

def main():
    parser = argparse.ArgumentParser(description="Prepare dataset for CogVideo.")

    parser.add_argument('--input_videos_dir', type=str, required=True, help='Directory containing input videos.')
    parser.add_argument('--output_dataset_dir', type=str, required=True, help='Output dataset directory.')
    parser.add_argument('--max_videos', type=int, default=None, help='Maximum number of videos to process.')
    args = parser.parse_args()

    input_videos_dir = args.input_videos_dir
    output_dataset_dir = args.output_dataset_dir
    max_videos = args.max_videos

    # Create output directories
    os.makedirs(output_dataset_dir, exist_ok=True)
    videos_output_dir = os.path.join(output_dataset_dir, 'videos')
    os.makedirs(videos_output_dir, exist_ok=True)

    # Prepare prompt.txt and videos.txt
    prompt_txt_path = os.path.join(output_dataset_dir, 'prompt.txt')
    videos_txt_path = os.path.join(output_dataset_dir, 'videos.txt')

    with open(prompt_txt_path, 'w') as prompt_file, open(videos_txt_path, 'w') as videos_file:
        video_files = [f for f in os.listdir(input_videos_dir) if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]
        video_files.sort()

        if max_videos is not None:
            video_files = video_files[:max_videos]

        for idx, video_filename in enumerate(video_files):
            print(f'Processing video {idx + 1}/{len(video_files)}: {video_filename}')
            input_video_path = os.path.join(input_videos_dir, video_filename)

            # Process video
            success = process_video(input_video_path, videos_output_dir, idx)

            if success:
                # Write to videos.txt
                video_relative_path = f'videos/{str(idx).zfill(5)}.mp4'
                videos_file.write(video_relative_path + '\n')
                # Write an empty line or placeholder to prompt.txt
                prompt_file.write('\n')  # Empty line for manual captioning
                # Alternatively, write a placeholder:
                # prompt_file.write(f'Caption for video {idx}\n')
            else:
                print(f'Failed to process video: {video_filename}')

    print("Dataset preparation completed.")
    print("Note: 'prompt.txt' has been created with empty lines. You can fill in captions manually.")


def process_video(video_path, output_dir, idx):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f'Cannot open video: {video_path}')
        return False

    # Get original video properties
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    original_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    if original_frame_count <= 0:
        print(f'No frames found in video: {video_path}')
        return False

    # Adjust resolution to be divisible by 32
    new_width = (original_width // 32) * 32
    new_height = (original_height // 32) * 32
    if new_width <= 0 or new_height <= 0:
        print(f'Invalid video resolution after adjustment: {new_width}x{new_height}')
        return False

    # Adjust frame count to be 4k or 4k+1 (for some integer k)
    target_frame_count = get_nearest_acceptable_frame_count(original_frame_count)
    if target_frame_count <= 0:
        print(f'Invalid target frame count: {target_frame_count}')
        return False

    # Read frames and store them
    frames = []
    while len(frames) < original_frame_count:
        ret, frame = cap.read()
        if not ret:
            break
        # Resize frame
        resized_frame = cv2.resize(frame, (new_width, new_height))
        frames.append(resized_frame)

    cap.release()

    if len(frames) == 0:
        print(f'No frames extracted from video: {video_path}')
        return False

    # Resample frames to match target frame count
    frames = resample_frames(frames, target_frame_count)

    # Write processed video
    output_video_filename = os.path.join(output_dir, f'{str(idx).zfill(5)}.mp4')

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = fps if fps > 0 else 24  # Default to 24 FPS if original FPS is invalid

    out = cv2.VideoWriter(output_video_filename, fourcc, fps, (new_width, new_height))

    for frame in frames:
        out.write(frame)

    out.release()

    return True


def get_nearest_acceptable_frame_count(frame_count):
    # Find the nearest acceptable frame count (4k or 4k+1)
    k = frame_count // 4
    options = [4 * k, 4 * k + 1, 4 * (k + 1), 4 * (k - 1) + 1]
    # Remove negative options
    options = [count for count in options if count > 0]
    # Choose the option closest to the original frame count
    nearest_frame_count = min(options, key=lambda x: abs(x - frame_count))

    # Ensure the frame count is at least 4
    if nearest_frame_count < 4:
        nearest_frame_count = 4

    return nearest_frame_count


def resample_frames(frames, target_frame_count):
    original_frame_count = len(frames)
    if original_frame_count == target_frame_count:
        return frames
    else:
        # Resample frames to target frame count
        indices = np.linspace(0, original_frame_count - 1, target_frame_count).astype(int)
        resampled_frames = [frames[i] for i in indices]
        return resampled_frames


if __name__ == '__main__':
    main()
