import argparse
import logging
import os

import cv2
import numpy as np
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_nearest_frame_count(frame_count, allowed_counts):
    """
    Finds the closest allowed frame count that is less than or equal to the given frame count.

    Args:
        frame_count (int): Number of frames in the input video.
        allowed_counts (list): List of allowed frame counts.

    Returns:
        int: The nearest allowed frame count.
    """
    for count in sorted(allowed_counts, reverse=True):
        if frame_count >= count:
            return count
    return min(allowed_counts)


def get_target_resolution(width, height, allowed_resolutions):
    """
    Finds the closest allowed resolution while maintaining the aspect ratio.

    Args:
        width (int): Original video width.
        height (int): Original video height.
        allowed_resolutions (list): List of allowed resolutions.

    Returns:
        tuple: (new_width, new_height) adjusted to be within allowed sizes.
    """
    max_size = max(width, height)
    for size in sorted(allowed_resolutions):
        if max_size <= size:
            scale_ratio = size / max_size
            new_width = int(round((width * scale_ratio) / 32) * 32)
            new_height = int(round((height * scale_ratio) / 32) * 32)
            return new_width, new_height

    # Scale down if larger than the max allowed resolution
    max_allowed = max(allowed_resolutions)
    scale_ratio = max_allowed / max_size
    new_width = int(round((width * scale_ratio) / 32) * 32)
    new_height = int(round((height * scale_ratio) / 32) * 32)
    return new_width, new_height


def process_video(video_path, output_path, allowed_frame_counts, allowed_resolutions):
    """
    Processes a single video by adjusting frame count and resolution, then saves it.

    Args:
        video_path (str): Path to input video.
        output_path (str): Path to save processed video.
        allowed_frame_counts (list): List of allowed frame counts.
        allowed_resolutions (list): List of allowed resolutions.
    """
    logger.info(f"Processing video: {video_path}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Failed to open video: {video_path}")
        return

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    orig_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    logger.info(
        f"Original properties: {frame_count} frames, {orig_width}x{orig_height}, {fps:.2f} FPS"
    )

    target_frame_count = get_nearest_frame_count(frame_count, allowed_frame_counts)
    target_width, target_height = get_target_resolution(
        orig_width, orig_height, allowed_resolutions
    )

    logger.info(
        f"Target properties: {target_frame_count} frames, {target_width}x{target_height}"
    )

    # Read frames and resize them
    frames = []
    for i in range(target_frame_count):
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (target_width, target_height))
        frames.append(frame)

    cap.release()

    # Write output video
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (target_width, target_height))
    for frame in frames:
        out.write(frame)
    out.release()

    logger.info(f"Saved processed video: {output_path}")


def process_videos(input_dir, output_dir):
    """
    Recursively processes all videos in the specified directory and its subdirectories.

    Args:
        input_dir (str): Path to the directory containing input videos.
        output_dir (str): Path to save processed videos and metadata.
    """
    if not os.path.exists(input_dir):
        logger.error(f"Input directory not found: {input_dir}")
        return

    allowed_frame_counts = [17, 49, 61, 129]
    allowed_resolutions = [512, 768, 960, 1280]

    videos_output_dir = os.path.join(output_dir, "videos")
    os.makedirs(videos_output_dir, exist_ok=True)

    videos_txt = []
    prompts_txt = []

    logger.info(f"Scanning directory (including subdirectories): {input_dir}")

    # Recursively find video files
    video_files = []
    for root, _, files in os.walk(input_dir):  # <-- Now searches subdirectories too!
        for file in files:
            if file.lower().endswith((".mp4", ".avi", ".mov", ".mkv")):
                video_files.append(os.path.join(root, file))

    if not video_files:
        logger.warning(f"No video files found in {input_dir}")
        return

    logger.info(f"Found {len(video_files)} video(s) to process.")

    for idx, video_path in enumerate(
        tqdm(video_files, desc="Processing videos"), start=1
    ):
        # Preserve subdirectory structure in output
        relative_path = os.path.relpath(video_path, input_dir)
        output_video_path = os.path.join(videos_output_dir, relative_path)

        os.makedirs(
            os.path.dirname(output_video_path), exist_ok=True
        )  # Ensure subdirectories exist in output

        logger.info(f"Processing ({idx}/{len(video_files)}): {video_path}")
        process_video(
            video_path, output_video_path, allowed_frame_counts, allowed_resolutions
        )

        videos_txt.append(os.path.relpath(output_video_path, output_dir))
        prompts_txt.append("")  # Placeholder for prompts

    # Save metadata files
    with open(os.path.join(output_dir, "videos.txt"), "w") as f:
        for line in videos_txt:
            f.write(line + "\n")

    with open(os.path.join(output_dir, "prompt.txt"), "w") as f:
        for line in prompts_txt:
            f.write(line + "\n")

    logger.info(f"Metadata saved: videos.txt, prompt.txt")
    logger.info("Processing complete.")


def main():
    """
    Main function to execute the video processing pipeline.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_videos_dir",
        type=str,
        required=True,
        help="Path to input video directory",
    )
    parser.add_argument(
        "--output_dataset_dir",
        type=str,
        required=True,
        help="Path to output dataset directory",
    )
    args = parser.parse_args()

    logger.info(f"Starting processing for directory: {args.input_videos_dir}")
    process_videos(args.input_videos_dir, args.output_dataset_dir)
    logger.info("Processing finished.")


if __name__ == "__main__":
    main()
