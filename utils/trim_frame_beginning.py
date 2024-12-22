import os
import subprocess
import sys
from multiprocessing import Pool


def get_frame_rate(video_path):
    """Get the frame rate of the video using ffprobe."""
    command = [
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-of',
        'default=noprint_wrappers=1:nokey=1', '-show_entries',
        'stream=avg_frame_rate', video_path
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Failed to get frame rate for {video_path}. Error: {result.stderr}")
        return None
    frame_rate_str = result.stdout.strip()
    if frame_rate_str:
        nums = frame_rate_str.split('/')
        if len(nums) == 2 and nums[1] != '0':
            return float(nums[0]) / float(nums[1])
        else:
            return float(nums[0])
    else:
        return None


def trim_video(input_path, num_frames):
    # Trim the first num_frames from the video at input_path and overwrite the file
    # Get frame rate to calculate time to trim
    frame_rate = get_frame_rate(input_path)
    if frame_rate is None:
        print(f"Could not determine frame rate for {input_path}. Skipping.")
        return
    # Calculate time to trim in seconds
    time_to_trim = num_frames / frame_rate
    # Use FFmpeg to trim the video (with re-encoding)
    # Get video codec
    video_codec = get_video_codec(input_path)
    # Get audio codec
    audio_codec = get_audio_codec(input_path)
    # Create a temporary output file
    temp_output_path = input_path + '.tmp'
    command = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-i', input_path,
        '-ss', f'{time_to_trim}',
        '-c:v', video_codec,
        '-c:a', audio_codec,
        '-movflags', '+faststart',
        temp_output_path
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        # Replace the original file with the trimmed file
        os.replace(temp_output_path, input_path)
        print(f"Trimmed {input_path}")
    else:
        print(f"Failed to trim {input_path}. Error: {result.stderr}")
        if os.path.exists(temp_output_path):
            os.remove(temp_output_path)


def get_video_codec(video_path):
    """Get the video codec of the input video."""
    command = [
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
        'stream=codec_name', '-of', 'default=noprint_wrappers=1:nokey=1', video_path
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    codec = result.stdout.strip()
    if codec:
        return codec
    else:
        return 'libx264'  # Default to libx264 if codec detection fails


def get_audio_codec(video_path):
    """Get the audio codec of the input video."""
    command = [
        'ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries',
        'stream=codec_name', '-of', 'default=noprint_wrappers=1:nokey=1', video_path
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    codec = result.stdout.strip()
    if codec:
        # Map known codecs to FFmpeg codecs
        codec_mapping = {
            'aac': 'aac',
            'mp3': 'libmp3lame',
            'ac3': 'ac3',
            'flac': 'flac',
            'vorbis': 'libvorbis',
            'opus': 'libopus',
            # Add more mappings as needed
        }
        return codec_mapping.get(codec, 'aac')  # Default to 'aac' if codec not in mapping
    else:
        return 'aac'  # Default to 'aac' if no audio stream or detection fails


def process_video(args):
    input_path, output_path, num_frames = args
    trim_video(input_path, output_path, num_frames)


def main():
    # Check for the number of frames argument
    if len(sys.argv) > 1:
        try:
            num_frames = int(sys.argv[1])
        except ValueError:
            print("Invalid number of frames specified. Using default value of 5.")
            num_frames = 5
    else:
        num_frames = 5  # Default number of frames to trim

    print(f"Trimming {num_frames} frame(s) from the beginning of each video.")

    # Fixed input directory
    input_directory = os.path.join(os.getcwd(), "outputs", "video")
    # Supported video extensions
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.ts')
    # List to hold arguments for each video file
    args_list = []
    # Walk through subdirectories in input_directory
    for root, dirs, files in os.walk(input_directory):
        for file in files:
            if file.lower().endswith(video_extensions):
                input_path = os.path.join(root, file)
                args_list.append((input_path, num_frames))
    # Use multiprocessing to process videos in parallel
    if args_list:
        with Pool() as pool:
            pool.map(process_video, args_list)
    else:
        print("No video files found to process.")


if __name__ == "__main__":
    main()
