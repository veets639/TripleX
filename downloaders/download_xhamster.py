import requests
import re
import json
import os
import shutil
import subprocess
from multiprocessing import Pool
from urllib.parse import urljoin
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('xhamster_downloader.log'),
        logging.StreamHandler()
    ]
)

def get_id_from_url(url):
    pattern = r'/videos/.+?-([\w\d]+)(?:\?|$)'
    match = re.search(pattern, url)
    if match:
        video_id = match.group(1)
        logging.info(f"Video ID: {video_id}")
        return video_id
    else:
        logging.error("No match found for video ID")
        return None

def get_master_playlists(video_id):
    # Visit embed page
    base_url = "https://xhamster.com/embed/"
    full_url = base_url + video_id
    logging.info(f"Fetching embed page: {full_url}")
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/100.0.4844.84 Safari/537.36"
        ),
        "Referer": "https://xhamster.com/"
    }
    try:
        response = requests.get(full_url, headers=headers)
        if response.status_code != 200:
            logging.error(f"Failed to fetch embed page: HTTP {response.status_code}")
            return None
        # Adjust the regex pattern to match the new structure
        script_content = re.search(
            r'window\.initials\s*=\s*({.*?});\s*</script>', 
            response.text, re.DOTALL
        )
        if not script_content:
            # Try alternative pattern
            script_content = re.search(
                r'window\.xplayerSettings\s*=\s*({.*?});\s*</script>', 
                response.text, re.DOTALL
            )
        if script_content:
            json_str = script_content.group(1)
            # Clean up JSON string if necessary
            json_str = json_str.strip()
            json_data = json.loads(json_str)
            playlists = {}
            # Navigating the JSON to get 'sources'
            if 'xplayerSettings' in json_data:
                sources = json_data['xplayerSettings'].get('sources', {})
            else:
                sources = json_data.get('sources', {})
            section = sources.get('standard', {})
            if not section:
                logging.error("No 'standard' section found in sources.")
                return None
            for codec in ['h264', 'av1']:
                codec_data = section.get(codec)
                if not codec_data:
                    logging.info(f"No {codec.upper()} data found in 'standard' section.")
                    continue
                if isinstance(codec_data, list):
                    # For 'standard' section
                    if codec_data and 'url' in codec_data[0]:
                        playlist_url = codec_data[0]['url']
                        logging.info(f"Found {codec.upper()} standard playlist: {playlist_url}")
                        playlists[codec] = playlist_url
                elif isinstance(codec_data, dict):
                    # Handle if it's a dict (just in case)
                    if 'url' in codec_data:
                        playlist_url = codec_data['url']
                        logging.info(f"Found {codec.upper()} standard playlist: {playlist_url}")
                        playlists[codec] = playlist_url
            if playlists:
                return playlists
            else:
                logging.error("No playlists found in JSON data.")
                return None
        else:
            logging.error("No JSON data found on the embed page.")
            return None
    except Exception as e:
        logging.error(f"An error occurred while fetching the embed page: {str(e)}")
        return None

def get_best_quality_stream(master_playlist_url, min_vertical_resolution=144, max_vertical_resolution=2160):
    # Fetch the playlist
    logging.info(f"Fetching master playlist: {master_playlist_url}")
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/100.0.4844.84 Safari/537.36"
        ),
        "Referer": "https://xhamster.com/"
    }
    try:
        response = requests.get(master_playlist_url, headers=headers)
        if response.status_code != 200:
            logging.error(f"Failed to fetch master playlist: HTTP {response.status_code}")
            return None
        playlist_text = response.text
        # Parse the M3U8 file to find the streams and resolutions
        master_lines = playlist_text.strip().split('\n')
        streams = []
        for i in range(len(master_lines)):
            if master_lines[i].startswith('#EXT-X-STREAM-INF'):
                match = re.search(r'RESOLUTION=(\d+)x(\d+)', master_lines[i])
                if match:
                    width = int(match.group(1))
                    height = int(match.group(2))
                    # Next line should be the URL
                    if i + 1 < len(master_lines):
                        url = master_lines[i + 1].strip()
                        streams.append({'width': width, 'height': height, 'url': url})
        if not streams:
            logging.error("No streams found in master playlist.")
            return None
        # Get the best quality among the streams within the resolution range
        streams_within_range = [s for s in streams if min_vertical_resolution <= s['height'] <= max_vertical_resolution]
        if not streams_within_range:
            logging.error(f"No streams found within the resolution range {min_vertical_resolution}-{max_vertical_resolution}p.")
            return None
        best_stream = max(streams_within_range, key=lambda s: s['height'])
        best_quality_url = best_stream['url']
        logging.info(f"Best quality stream URL: {best_quality_url}")
        # Handle the URL if it's relative
        if not best_quality_url.startswith('http'):
            final_url = urljoin(master_playlist_url, best_quality_url)
        else:
            final_url = best_quality_url
        return final_url
    except Exception as e:
        logging.error(f"An error occurred while fetching the master playlist: {str(e)}")
        return None
def download_and_process_h264(full_variant_url, title, video_id, destination_folder):
    logging.info(f"Fetching H264 variant playlist: {full_variant_url}")
    response = requests.get(full_variant_url)
    variant_playlist_lines = response.text.split('\n')
    segment_urls = [line.strip() for line in variant_playlist_lines if line and not line.startswith('#')]
    segment_args = [(urljoin(full_variant_url, segment), f'segment_{i}.ts') for i, segment in enumerate(segment_urls)]

    logging.info(f"Downloading and processing {len(segment_args)} segments.")

    # Create a pool of workers and process segments in parallel
    with Pool() as pool:
        results = pool.map(download_and_process_segment_h264, segment_args)

    # Keep only successful segments
    segments = [filename for success, filename in results if success]
    failed_segments = [filename for success, filename in results if not success]

    if failed_segments:
        logging.warning(f"{len(failed_segments)} segments failed and will be skipped.")

    if not segments:
        logging.error("All segments failed to download/process. Cannot proceed.")
        return

    # Write the file list for FFmpeg concatenation
    with open('file_list.txt', 'w') as f:
        for filename in segments:
            if os.path.exists(filename):
                f.write(f"file '{filename}'\n")
            else:
                logging.warning(f"Segment file not found and will be skipped: {filename}")

    # Concatenate segments using FFmpeg
    output_video = os.path.join(destination_folder, f"{title}.mp4")
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', 'file_list.txt',
        '-c', 'copy', output_video
    ])

    logging.info(f"Video saved as: {output_video}")

    # Clean up temporary files
    for filename in segments:
        try:
            os.remove(filename)
        except OSError as e:
            logging.error(f"Failed to remove segment file {filename}: {e}")

    os.remove('file_list.txt')

def download_and_process_segment_h264(args):
    url, output_filename = args
    output_filename = os.path.abspath(output_filename)
    max_retries = 3  # Number of retry attempts
    retry_delay = 5  # Delay between retries in seconds
    for attempt in range(max_retries):
        try:
            logging.debug(f"Downloading from {url} to {output_filename}")
            command = [
                'ffmpeg', '-y', '-i', url, '-an', '-c:v', 'copy', output_filename
            ]
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logging.debug(f"Successfully processed {output_filename}")
            return (True, output_filename)
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to process {output_filename} on attempt {attempt + 1}. Error: {e.stderr.decode()}")
            if attempt < max_retries - 1:
                logging.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logging.error(f"Exceeded maximum retries for {output_filename}. Skipping this segment.")
    return (False, output_filename)

def download_and_process_av1(master_playlist_url, title, video_id, destination_folder):
    # Fetch the master playlist
    logging.info("Fetching the AV1 master playlist")
    response = requests.get(master_playlist_url)
    master_playlist_lines = response.text.splitlines()

    # Extract variant playlist URLs
    variant_playlists = {}
    for i in range(len(master_playlist_lines)):
        if master_playlist_lines[i].startswith('#EXT-X-STREAM-INF'):
            bandwidth_match = re.search(r'BANDWIDTH=(\d+)', master_playlist_lines[i])
            resolution_match = re.search(r'RESOLUTION=(\d+x\d+)', master_playlist_lines[i])
            if bandwidth_match and resolution_match:
                bandwidth = int(bandwidth_match.group(1))
                resolution = resolution_match.group(1)
                url = master_playlist_lines[i + 1].strip()
                variant_playlists[(bandwidth, resolution)] = url

    if not variant_playlists:
        logging.error("No variant playlists found in the AV1 master playlist.")
        return

    # Select the highest bandwidth variant
    selected_variant_url = variant_playlists[max(variant_playlists)]
    full_variant_url = urljoin(master_playlist_url, selected_variant_url)

    logging.info(f"Selected AV1 variant playlist: {full_variant_url}")

    # Download the initialization segment
    init_segment_url = full_variant_url.replace('.m3u8', '/init-v1-a1.mp4')
    download_file(init_segment_url, 'init-v1-a1.mp4')

    # Download the variant playlist
    response = requests.get(full_variant_url)
    variant_playlist_lines = response.text.split('\n')

    # Filter out the segment URLs
    segment_urls = [line.strip() for line in variant_playlist_lines if line and not line.startswith('#')]

    logging.info(f"Downloading and processing {len(segment_urls)} AV1 segments.")

    # Process all segments
    process_all_segments_av1(segment_urls, full_variant_url, title, video_id, destination_folder)

def download_file(url, filename):
    logging.info(f"Downloading file from {url}")
    headers = {"Referer": "https://xhamster.com/"}
    response = requests.get(url, stream=True, headers=headers)
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

def process_all_segments_av1(segment_urls, full_variant_url, title, video_id, destination_folder, init_file='init-v1-a1.mp4'):
    temp_files = []  # List to track all temporary files for cleanup
    segment_args = [(merge_urls_av1(full_variant_url, segment_url), index, init_file) for index, segment_url in enumerate(segment_urls)]
    # Create a pool of workers and process segments in parallel
    with Pool() as pool:
        output_files = pool.starmap(process_segment_av1, segment_args)

    # Filter out None values (failed segments)
    output_files = [f for f in output_files if f is not None]

    if not output_files:
        logging.error("All segments failed to download/process. Cannot proceed.")
        return

    temp_files.extend(output_files)

    # Write all filenames to file_list.txt for concatenation
    with open('file_list.txt', 'w') as f:
        for filename in output_files:
            f.write(f"file '{filename}'\n")

    # Concatenate the segments into the final video
    output_video = os.path.join(destination_folder, f"{title}.mp4")
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', 'file_list.txt',
        '-c', 'copy', output_video
    ])
    logging.info(f"Video saved as: {output_video}")

    # Cleanup temporary files
    for filename in temp_files:
        os.remove(filename)
    if os.path.exists(init_file):
        os.remove(init_file)
    os.remove('file_list.txt')
    logging.info("Cleanup completed.")

def process_segment_av1(url, index, init_file='init-v1-a1.mp4'):
    segment_filename = f'segment_{index}.m4s'
    output_filename = f'output_segment_{index}.mp4'
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            download_file(url, segment_filename)
            logging.debug(f"Processing segment: {segment_filename} into {output_filename}")
            # Concatenate init file and segment
            concat_input = f"concat:{init_file}|{segment_filename}"
            subprocess.run([
                'ffmpeg', '-y', '-i', concat_input,
                '-c', 'copy', '-an',
                output_filename
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            os.remove(segment_filename)
            return output_filename
        except Exception as e:
            logging.error(f"Failed to process segment {url} on attempt {attempt + 1}. Error: {e}")
            if os.path.exists(segment_filename):
                os.remove(segment_filename)
            if attempt < max_retries - 1:
                logging.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logging.error(f"Exceeded maximum retries for segment {url}. Skipping this segment.")
    return None  # Indicate failure

def merge_urls_av1(base_url, relative_url):
    # Construct the full URL for the segment
    base_dir = base_url.rsplit('/', 1)[0]
    merged_url = urljoin(base_dir + '/', relative_url)
    return merged_url

def main():
    # Check for URL argument
    if len(sys.argv) < 2:
        print("Usage: python download_xhamster.py <video_url>")
        return
    url = sys.argv[1]

    # Set the destination folder to outputs/video
    destination_folder = os.path.join(os.getcwd(), "outputs", "video")
    os.makedirs(destination_folder, exist_ok=True)

    video_id = get_id_from_url(url)
    if not video_id:
        logging.error("Failed to extract video ID from URL.")
        return

    playlists = get_master_playlists(video_id)
    if not playlists:
        logging.error("Failed to get master playlists.")
        return

    # Define your resolution preferences
    min_vertical_resolution = 144
    max_vertical_resolution = 2160

    # Get the video title from the page (optional enhancement)
    # For simplicity, we'll use the video ID as the title
    title = video_id

    # Process H264 stream if available
    if 'h264' in playlists:
        logging.info("Processing H264 stream.")
        master_playlist_url = playlists['h264']
        best_stream_url = get_best_quality_stream(
            master_playlist_url, min_vertical_resolution, max_vertical_resolution
        )
        if best_stream_url:
            download_and_process_h264(best_stream_url, title, video_id, destination_folder)
        else:
            logging.error("Failed to get best H264 stream.")
    else:
        logging.warning("H264 stream not available.")

    # Process AV1 stream if available
    if 'av1' in playlists:
        logging.info("Processing AV1 stream.")
        master_playlist_url = playlists['av1']
        best_stream_url = get_best_quality_stream(
            master_playlist_url, min_vertical_resolution, max_vertical_resolution
        )
        if best_stream_url:
            download_and_process_av1(best_stream_url, title, video_id, destination_folder)
        else:
            logging.error("Failed to get best AV1 stream.")
    else:
        logging.warning("AV1 stream not available.")

if __name__ == "__main__":
    main()
