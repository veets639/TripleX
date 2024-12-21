import os
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from scenedetect.video_splitter import split_video_ffmpeg

def split_video_into_scenes(video_path, output_dir, threshold=30.0, min_scene_len=15):
    # Create a video manager
    video_manager = VideoManager([video_path])
    # Create a scene manager and add the detector
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold, min_scene_len=min_scene_len))
    # Base timecode
    base_timecode = video_manager.get_base_timecode()
    # Start and detect scenes
    try:
        video_manager.start()
        scene_manager.detect_scenes(frame_source=video_manager)
        scene_list = scene_manager.get_scene_list(base_timecode)
        print(f"{len(scene_list)} scenes detected!")
        # Split video using FFmpeg
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        split_video_ffmpeg([video_path], scene_list, output_dir=output_dir, suppress_output=False)
        print(f"Video has been split into scenes and saved in '{output_dir}'")
    finally:
        video_manager.release()

def main():
    # Fixed input directory
    input_directory = os.path.join(os.getcwd(), "outputs", "video")
    # Process all video files in input_directory
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.ts')
    for file_name in os.listdir(input_directory):
        if file_name.lower().endswith(video_extensions):
            video_path = os.path.join(input_directory, file_name)
            # Create subdirectory for output scenes
            video_name_without_ext = os.path.splitext(file_name)[0]
            output_dir = os.path.join(input_directory, video_name_without_ext)
            print(f"Processing video '{video_path}'")
            # Call split_video_into_scenes
            split_video_into_scenes(video_path, output_dir)
    print("All videos processed.")

if __name__ == "__main__":
    main()