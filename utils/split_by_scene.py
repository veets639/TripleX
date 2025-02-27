import os
import subprocess
from pathlib import Path

from scenedetect import SceneManager, VideoManager
from scenedetect.detectors import ContentDetector
from scenedetect.video_splitter import split_video_ffmpeg


def is_video_valid(video_path):
    """Check if the video file is valid using ffmpeg."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(video_path), "-f", "null", "-"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:  # If ffmpeg detects an issue, return False
            print(f"Invalid video detected: {video_path}. Removing it...")
            os.remove(video_path)  # Delete the bad file
            return False
    except Exception as e:
        print(f"Error checking video {video_path}: {e}")
        os.remove(video_path)  # Ensure file is deleted if check fails
        return False
    return True


def split_video_into_scene_clips(
    video_path, output_dir, threshold=15.0, min_scene_len=15
):
    """Split video into scenes using SceneDetect."""
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(
        ContentDetector(threshold=threshold, min_scene_len=min_scene_len)
    )

    base_timecode = video_manager.get_base_timecode()

    try:
        video_manager.start()
        scene_manager.detect_scenes(frame_source=video_manager)
        scene_list = scene_manager.get_scene_list(base_timecode)
        print(f"{len(scene_list)} scenes detected!")

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        split_video_ffmpeg(
            [video_path], scene_list, output_dir=output_dir, suppress_output=False
        )
        print(f"Video split into scenes and saved in '{output_dir}'")
    finally:
        video_manager.release()


def main():
    input_directory = Path(os.getcwd()) / "data" / "videos"
    scenes_output_directory = Path(os.getcwd()) / "data" / "clips"

    if not scenes_output_directory.exists():
        scenes_output_directory.mkdir(parents=True, exist_ok=True)

    video_extensions = (".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".ts")

    for file_name in os.listdir(input_directory):
        video_path = input_directory / file_name

        if not file_name.lower().endswith(video_extensions):
            continue  # Skip non-video files

        if not is_video_valid(video_path):
            continue  # If video is bad, it is deleted & skipped

        video_name_without_ext = video_path.stem
        output_dir = scenes_output_directory / video_name_without_ext

        print(f"Processing video '{video_path}'")
        split_video_into_scene_clips(video_path, output_dir)

    print("All videos processed.")


if __name__ == "__main__":
    main()
