import os
import sys
from pathlib import Path

# Define the base directory
BASE_DIR = Path(__file__).resolve().parent.parent / "data"

# Extension normalization map
EXTENSION_MAP = {
    "jpeg": "jpg",
    "JPG": "jpg",
    "JPEG": "jpg",
    "PNG": "png",
    "Mp4": "mp4",
    "MP4": "mp4",
    "GIF": "gif",
    "Tiff": "tiff",
    "TIFF": "tiff",
    "bmp": "bmp",
    "BMP": "bmp",
}


# Get all files recursively
def get_all_files(directory):
    return sorted([f for f in directory.rglob("*") if f.is_file()])


# Generate new file names
def rename_files():
    all_files = get_all_files(BASE_DIR)

    # Sort files to ensure deterministic naming
    all_files.sort(key=lambda x: x.stat().st_mtime)  # Sort by modification time

    counter = 1
    renamed_files = set()  # To track already used names

    for file in all_files:
        ext = file.suffix.lower().lstrip(".")  # Extract extension and normalize
        normalized_ext = EXTENSION_MAP.get(ext, ext)  # Normalize extension if in map

        new_filename = f"{counter:05d}.{normalized_ext}"  # Zero-padded name
        new_path = file.parent / new_filename  # Full path

        # Ensure no conflicts
        while new_path in renamed_files:
            counter += 1
            new_filename = f"{counter:05d}.{normalized_ext}"
            new_path = file.parent / new_filename

        # Rename file
        file.rename(new_path)
        renamed_files.add(new_path)

        print(f"Renamed: {file} -> {new_path}")
        counter += 1


if __name__ == "__main__":
    print(f"Starting renaming process in: {BASE_DIR}")
    rename_files()
    print("Renaming completed.")
