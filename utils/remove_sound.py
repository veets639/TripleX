import logging
import os
import subprocess
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def remove_audio_from_video(input_video: str, output_video: str) -> bool:
    """
    Removes the audio track from a video using FFmpeg.

    Args:
        input_video (str): Path to the input (backup) video file.
        output_video (str): Path to save the new video without audio.

    Returns:
        bool: True if processing succeeds, False otherwise.
    """
    try:
        logger.info(f"Starting audio removal: {input_video} -> {output_video}")

        command = [
            "ffmpeg",
            "-i",
            input_video,  # Use .bak file as input
            "-an",  # Remove audio
            "-c:v",
            "copy",  # Copy video stream without re-encoding
            output_video,  # Output file (same as original)
        ]
        subprocess.run(
            command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        logger.info(f"Audio removed successfully: {output_video}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to process {input_video}: {e}", exc_info=True)
        return False


def process_videos_in_directory(target_dir: str):
    """
    Recursively processes all video files in the given directory by removing their audio.

    Args:
        target_dir (str): The root directory containing video files.
    """
    if not os.path.exists(target_dir):
        logger.error(f"Directory not found: {target_dir}")
        return

    video_extensions = (".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".ts")

    logger.info(f"Scanning directory: {target_dir}")

    video_files = []
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.lower().endswith(video_extensions):
                video_files.append(os.path.join(root, file))

    if not video_files:
        logger.warning(f"No video files found in {target_dir}")
        return

    logger.info(f"Found {len(video_files)} video(s) to process.")

    for idx, input_video_path in enumerate(video_files, start=1):
        logger.info(f"Processing ({idx}/{len(video_files)}): {input_video_path}")

        backup_video_path = input_video_path + ".bak"

        if os.path.exists(backup_video_path):
            logger.warning(f"Skipping {input_video_path}: Backup file already exists.")
            continue

        # Move original file to .bak first
        os.rename(input_video_path, backup_video_path)
        logger.info(f"Moved original file to backup: {backup_video_path}")

        # Remove audio and replace the original file
        if remove_audio_from_video(backup_video_path, input_video_path):
            logger.info(f"Successfully removed audio from {input_video_path}")
        else:
            logger.error(f"Failed to process {input_video_path}")


def main():
    """
    Main function to execute the video processing pipeline.
    """
    if len(sys.argv) != 2:
        logger.error("Usage: python utils/remove_sound.py <video_directory>")
        sys.exit(1)

    target_directory = sys.argv[1]
    logger.info(f"Starting processing for directory: {target_directory}")
    process_videos_in_directory(target_directory)
    logger.info("Processing complete.")


if __name__ == "__main__":
    main()
