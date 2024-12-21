# TripleX by NSFW API

Welcome to the **TripleX** repository! This project provides tools for downloading videos from supported websites and processing them using utilities like scene detection and trimming.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Directory Structure](#directory-structure)
- [Installation](#installation)
- [Usage](#usage)
  - [Downloading Videos](#downloading-videos)
  - [Splitting Videos by Scene](#splitting-videos-by-scene)
  - [Trimming Frames from Videos](#trimming-frames-from-videos)
- [Contributing](#contributing)
  - [Adding Downloaders for Other Sites](#adding-downloaders-for-other-sites)
  - [Adding New Utilities](#adding-new-utilities)
  - [General Contribution Steps](#general-contribution-steps)
- [License](#license)
- [Disclaimer](#disclaimer)

## Overview

**TripleX** is designed to help users download videos from supported websites and perform various processing tasks such as scene detection and trimming unwanted frames. The toolkit is modular, allowing for easy addition of new downloaders and utilities.

## Features

- **Video Downloaders**: Currently supports downloading videos from xHamster. Designed to be extensible for other sites.
- **Scene Detection**: Uses PySceneDetect to split videos into individual scenes.
- **Frame Trimming**: Trims a specified number of frames from the beginning of videos.
- **Modular Utilities**: Easily add new utilities or downloaders to extend functionality.

## Directory Structure

```plaintext
.
├── downloaders
│   └── download_xhamster.py
├── outputs
│   └── video
├── requirements.txt
└── utils
    ├── split_by_scene.py
    └── trim_frame_beginning.py
```

- **downloaders/**: Contains scripts for downloading videos from supported websites.
- **outputs/**: Default directory where videos and processed outputs are saved.
  - **video/**: Contains downloaded videos and processed scenes.
- **requirements.txt**: Lists the Python dependencies required for the project.
- **utils/**: Contains utility scripts for processing videos.

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/NSFW-API/TripleX.git
   cd triplex
   ```

2. **Create a Virtual Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install FFmpeg**

   - **macOS**:

     ```bash
     brew install ffmpeg
     ```

   - **Ubuntu/Debian**:

     ```bash
     sudo apt-get install ffmpeg
     ```

   - **Windows**:

     - Download FFmpeg from the [official website](https://ffmpeg.org/download.html).
     - Add FFmpeg to your system PATH.

## Usage

### Downloading Videos

The `download_xhamster.py` script allows you to download videos from xHamster.

**Note**: Ensure you comply with all legal requirements and terms of service when downloading content.

**Example Usage**:

```bash
python downloaders/download_xhamster.py <video_url>
```

- Replace `<video_url>` with the actual URL of the xHamster video.

**Instructions**:

1. **Run the Script**:

   ```bash
   python downloaders/download_xhamster.py <video_url>
   ```

2. **The Video** will be downloaded to `outputs/video`.

   - The script automatically saves the downloaded video in the `outputs/video` directory.
   - No additional input is required after providing the URL.

### Splitting Videos by Scene

The `split_by_scene.py` script splits all videos in `outputs/video` into scenes based on content detection.

**Example Usage**:

```bash
python utils/split_by_scene.py
```

**Instructions**:

- **Run the Script**:

  ```bash
  python utils/split_by_scene.py
  ```

- **Processing**:

  - The script processes all videos in `outputs/video`.
  - For each video, it creates a subdirectory within `outputs/video` named after the video file (without extension).
  - The split scenes are saved in the respective subdirectories.

**Notes**:

- **Content Detection Parameters**:

  - The script uses default parameters for scene detection (`threshold=30.0`, `min_scene_len=15`).
  - If you wish to adjust these parameters, you can modify the default values directly in the script.

### Trimming Frames from Videos

The `trim_frame_beginning.py` script trims a specified number of frames from the beginning of all videos in `outputs/video` and its subdirectories.

**Example Usage**:

```bash
python utils/trim_frame_beginning.py [num_frames]
```

- **`[num_frames]`** *(optional)*: The number of frames to trim from the beginning of each video. If not provided, the default is `5`.

**Instructions**:

- **Run the Script**:

  - To trim a specific number of frames:

    ```bash
    python utils/trim_frame_beginning.py 10
    ```

    - This command trims `10` frames from the beginning of each video.

  - To use the default number of frames (5):

    ```bash
    python utils/trim_frame_beginning.py
    ```

- **Processing**:

  - The script processes all videos in `outputs/video` and its subdirectories.
  - Overwrites the original video files after trimming.

**Notes**:

- **Backup**: Be cautious when overwriting files. It's recommended to keep backups if you might need the original files later.
- **Adjusting the Default Number of Frames**: If you frequently use a different number of frames, you can change the default value directly in the script.

## Contributing

Contributions are welcome! You can contribute to this project in the following ways:

### Adding Downloaders for Other Sites

1. **Create a New Downloader Script**: Follow the structure of `download_xhamster.py` to create a downloader for another site.

2. **Place the Script in the `downloaders/` Directory**.

3. **Testing**: Thoroughly test your script to ensure it works reliably.

4. **Documentation**: Update the README with instructions on how to use your new downloader.

5. **Submit a Pull Request**: Once you're ready, submit a pull request for review.

### Adding New Utilities

1. **Create a New Utility Script**: Develop your utility and place it in the `utils/` directory.

2. **Explain the Utility**: Provide clear instructions and examples on how to use your utility.

3. **Dependencies**: If your utility requires additional Python packages, update `requirements.txt`.

4. **Submit a Pull Request**: Include information about the utility and its usage in your pull request.

### General Contribution Steps

1. **Fork the Repository**: Click the "Fork" button at the top-right corner of the repository page.

2. **Clone Your Fork**:

   ```bash
   git clone https://github.com/NSFW-API/TripleX.git
   ```

3. **Create a New Branch**:

   ```bash
   git checkout -b feature/new-downloader
   ```

4. **Make Your Changes**: Add your downloader or utility script.

5. **Commit Your Changes**:

   ```bash
   git add .
   git commit -m "Add new downloader for ExampleSite"
   ```

6. **Push to Your Fork**:

   ```bash
   git push origin feature/new-downloader
   ```

7. **Open a Pull Request**: Go to the original repository and click "New Pull Request."

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

## Disclaimer

- **Legal Compliance**: This toolkit is intended for educational and personal use. Users are responsible for ensuring they comply with all applicable laws, regulations, and terms of service of the websites they interact with.

- **Content Rights**: Downloading and distributing copyrighted material without permission may infringe on intellectual property rights.

- **Adult Content**: Some downloaders may interact with websites containing adult content. Users should be aware of and comply with all legal age restrictions and content regulations in their jurisdiction.

- **No Liability**: The authors and contributors of this project are not liable for any misuse of the toolkit.

---

**Thank you for using TripleX!**

If you have any questions or need assistance, feel free to open an issue on the repository or reach out to the maintainers.

---

## Additional Notes

- **Logging**: The `download_xhamster.py` script logs its activities to `xhamster_downloader.log` in the project root directory. You can check this log file for detailed information in case of errors.

- **Error Handling**: The scripts include basic error handling to inform you of issues that may arise during processing. For more robust error handling, consider adding try-except blocks where appropriate.

- **Dependencies**: Ensure that all dependencies listed in `requirements.txt` are installed in your virtual environment. If you encounter issues, double-check that all required packages are installed.

```plaintext
# requirements.txt

requests
scenedetect
beautifulsoup4
```

- **FFmpeg**: FFmpeg is a crucial dependency for video processing in this toolkit. Ensure that it is correctly installed and accessible from your system's PATH.

- **Python Version**: This toolkit is developed for Python 3.x. Ensure you are using a compatible version of Python.

## Contact

- **Maintainer**: NSFW API
- **Email**: nsfwapi@gmail.com
- **GitHub Issues**: Please report any issues or bugs by opening an issue on the repository.

---

Feel free to reach out if you need any further assistance or have suggestions for improving the toolkit!