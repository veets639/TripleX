import argparse
import logging
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Change to logging.INFO for less output
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("scan_missing_txt.log"),  # Log to a file
        logging.StreamHandler(),  # Log to console
    ],
)

# Supported file types
VIDEO_EXTENSIONS = (".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".ts")
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")


def scan_directory(directory):
    """
    Scans the given directory and logs files that are missing corresponding .txt descriptions.
    """
    logging.info(f"Starting scan in directory: {directory}")

    # Convert directory to Path object for better handling
    directory = Path(directory)

    if not directory.exists():
        logging.error(f"Directory not found: {directory}")
        return

    # Iterate through files in the directory
    for file in directory.iterdir():
        if file.is_file():
            file_stem = file.stem  # Get filename without extension
            txt_file = directory / f"{file_stem}.txt"

            # Check for missing text files for video and image files
            if file.suffix.lower() in VIDEO_EXTENSIONS:
                logging.info(f"Video file detected: {file}")
                if not txt_file.exists():
                    logging.warning(f"Missing .txt file for video: {file}")

            elif file.suffix.lower() in IMAGE_EXTENSIONS:
                logging.info(f"Image file detected: {file}")
                if not txt_file.exists():
                    logging.warning(f"Missing .txt file for image: {file}")

    logging.info("Scan complete.")


def main():
    parser = argparse.ArgumentParser(
        description="Scan directory for video/image files missing .txt descriptions."
    )
    parser.add_argument(
        "--directory", required=True, help="Path to the directory to scan"
    )
    args = parser.parse_args()

    scan_directory(args.directory)


if __name__ == "__main__":
    main()
