import json
import logging
import os
import re
import subprocess
import sys
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from seleniumbase import Driver

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("spankbang_downloader.log"), logging.StreamHandler()],
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/100.0.4844.84 Safari/537.36"
    ),
    "Referer": "https://spankbang.com/",
}


def fetch_video_url(url):
    """
    Fetch the direct video URL from the SpankBang page using Selenium.

    Args:
        url (str): The URL of the SpankBang video page.

    Returns:
        str: The direct URL of the video if found, else None.
    """
    logging.info("Initializing Selenium driver...")
    driver = Driver(uc=True, headless=True)
    driver.get(url)

    logging.info("Fetching page source...")
    r_text = driver.page_source
    soup = BeautifulSoup(r_text, "lxml")
    driver.quit()

    logging.info("Extracting video URL...")
    video_url = None
    for video in soup.find_all("video"):
        src = video.get("src")
        if src and "blob" not in src and "gallery" not in src:
            video_url = src
            break

    if not video_url:
        logging.warning("No valid video URL found on the page.")
    return video_url


def download_video(stream_url, title, destination):
    """
    Downloads the video using FFmpeg.

    Args:
        stream_url (str): The direct URL of the video stream.
        title (str): The filename to save the video as.
        destination (str): The directory where the video will be saved.
    """
    logging.info(f"Downloading video: {stream_url}")
    os.makedirs(destination, exist_ok=True)
    output_path = os.path.join(destination, f"{title}.mp4")

    command = ["ffmpeg", "-y", "-i", stream_url, "-c", "copy", output_path]
    subprocess.run(command, check=True)
    logging.info(f"Video saved as: {output_path}")


def main():
    """
    Main function to download SpankBang videos based on URL input from the command line.

    Usage:
        python download_spankbang.py <video_url>
    """
    if len(sys.argv) < 2:
        print("Usage: python download_spankbang.py <video_url>")
        return

    video_url = sys.argv[1]
    destination_folder = os.path.join(os.getcwd(), "data", "videos")

    extracted_url = fetch_video_url(video_url)
    if not extracted_url:
        return

    title = (
        video_url.split("/")[3]
        .replace("+", "_")
        .replace("?", "")
        .replace("!", "")
        .replace(",", "")
    )
    download_video(extracted_url, title, destination_folder)


if __name__ == "__main__":
    main()
