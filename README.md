# TripleX by NSFW API

Welcome to the **TripleX** repository! This project provides tools for downloading videos from supported websites and processing them using utilities like scene detection, trimming, frame analysis, and dataset creation for model training.

Reddit: https://www.reddit.com/r/NSFW_API  
Discord: https://discord.gg/bW4Bhkfk

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Directory Structure](#directory-structure)
- [Installation](#installation)
- [Usage](#usage)
  - [Downloading Videos](#downloading-videos)
  - [Splitting Videos by Scene](#splitting-videos-by-scene)
  - [Trimming Frames from Videos](#trimming-frames-from-videos)
  - [Analyzing Frames](#analyzing-frames)
  - [Creating Datasets for Model Training](#creating-datasets-for-model-training)
- [Contributing](#contributing)
  - [Adding Downloaders for Other Sites](#adding-downloaders-for-other-sites)
  - [Adding New Utilities](#adding-new-utilities)
  - [General Contribution Steps](#general-contribution-steps)
- [License](#license)
- [Disclaimer](#disclaimer)
- [Additional Notes](#additional-notes)
- [Contact](#contact)

## Overview

**TripleX** is designed to help users download videos from supported websites and perform various processing tasks such as scene detection, trimming unwanted frames, analyzing frames using machine learning models, and creating datasets for training custom AI models. The toolkit is modular, allowing for easy addition of new downloaders and utilities.

## Features

- **Video Downloaders**: Currently supports downloading videos from xHamster. Designed to be extensible for other sites.
- **Scene Detection**: Uses PySceneDetect to split videos into individual scenes.
- **Frame Trimming**: Trims a specified number of frames from the beginning of videos.
- **Frame Analysis**: Analyzes frames extracted from videos using machine learning models for classification and detection.
- **Dataset Creation**: Facilitates the creation of datasets for training video generation AI models like Mochi LoRA.
- **Modular Utilities**: Easily add new utilities or downloaders to extend functionality.

## Directory Structure

```plaintext
.
├── LICENSE
├── README.md
├── downloaders
│   └── download_xhamster.py
├── models
├── outputs
│   ├── images
│   ├── scenes
│   └── video
├── requirements.txt
├── setup_models.py
└── utils
    ├── analyze_frames.py
    ├── extract_sharpest_frame.py
    ├── split_by_scene.py
    └── trim_frame_beginning.py
```

- **downloaders/**: Contains scripts for downloading videos from supported websites.
- **models/**: Directory where machine learning models will be downloaded and stored.
- **outputs/**: Default directory where videos and processed outputs are saved.
  - **video/**: Contains downloaded videos.
  - **scenes/**: Contains scenes extracted from videos.
  - **images/**: Contains extracted frames and analysis results.
- **requirements.txt**: Lists the Python dependencies required for the project.
- **setup_models.py**: Script to download machine learning models from Google Drive.
- **utils/**: Contains utility scripts for processing videos.
  - **split_by_scene.py**: Splits videos into scenes.
  - **trim_frame_beginning.py**: Trims frames from the beginning of videos.
  - **extract_sharpest_frame.py**: Extracts the sharpest frame from a video.
  - **analyze_frames.py**: Analyzes frames using machine learning models.

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/NSFW-API/TripleX.git
   cd TripleX
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

5. **Install TensorFlow and Additional Dependencies**

   - **TensorFlow**:

     ```bash
     pip install tensorflow
     ```

   - **OpenCV and NumPy**:

     ```bash
     pip install opencv-python numpy
     ```

6. **Set Up Machine Learning Models**

   The machine learning models required for frame analysis are stored externally due to their size. Use the provided script to download and set up the models.

   **Instructions**:

   - **Run the Model Setup Script**:

     ```bash
     python setup_models.py
     ```

     - This script will download the necessary model files from Google Drive and place them in the `models/` directory following the required structure.
     - Ensure you have an active internet connection.

   **Note**:

   - The `setup_models.py` script handles downloading large model files that cannot be included directly in the repository due to size limitations.

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
  - For each video, it creates a subdirectory within `outputs/scenes` named after the video file (without extension).
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

### Analyzing Frames

The `analyze_frames.py` script analyzes frames extracted from videos using machine learning models. It processes the sharpest frame from each video scene to classify and detect various elements.

**Example Usage**:

```bash
python utils/analyze_frames.py
```

**Instructions**:

1. **Ensure Scenes are Available**:

   - Before running the analysis, make sure you have split the videos into scenes using `split_by_scene.py`.
   - The scenes should be located in `outputs/scenes`.

2. **Ensure Models are Set Up**:

   - Run `setup_models.py` as described in the [Installation](#installation) section to download and set up the required models.

3. **Run the Script**:

   ```bash
   python utils/analyze_frames.py
   ```

4. **Processing**:

   - The script processes each video in `outputs/scenes`.
   - For each video, it extracts the sharpest frame using `extract_sharpest_frame.py`.
   - The extracted frame is analyzed using the following models:

     - **Pose Classification**: Classifies the pose in the frame.
     - **Watermark Detection**: Detects any watermarks present.
     - **Genital Detection**: Identifies regions in the frame.
     - **Penetration Detection**: Detects specific activities.

5. **Outputs**:

   - Analysis results are saved in JSON format in `outputs/images`.
   - The analyzed frames are also saved in `outputs/images`.

**Notes**:

- **Dependencies**:

  - Ensure that you have installed all necessary dependencies, including TensorFlow, OpenCV, and NumPy.

- **Model Requirements**:

  - The models are automatically downloaded and set up using `setup_models.py`.

- **Adjustable Parameters**:

  - The script processes all videos by default. You can modify it to process specific videos or frames as needed.

### Creating Datasets for Model Training

**TripleX** can be used to create customized datasets for training video generation AI models like **Mochi LoRA**. By processing and extracting frames from videos, you can generate datasets suitable for model training.

For a detailed guide on how to use this repository to create a dataset and train a Mochi LoRA model using Modal (a GPU app hosting platform), refer to the following article:

- **Guide**: [How to Train a Video Model Using TripleX and Mochi LoRA](https://civitai.com/articles/9966)

**Instructions**:

1. **Prepare Your Dataset**:

   - Use the utilities provided in **TripleX** to download videos, split them into scenes, and extract frames.
   - The frames and metadata generated can form the basis of your training dataset.

2. **Follow the Guide**:

   - The linked guide provides step-by-step instructions on how to process the dataset created with TripleX and train a Mochi LoRA model.
   - It includes information on setting up the training environment on Modal, configuring parameters, and running the training process.

**Notes**:

- **Model Training Considerations**:

  - Ensure that you have the rights and permissions to use the videos and frames for training purposes.
  - Be mindful of data privacy, legal compliance, and ethical considerations when creating and using datasets.

- **Compatibility**:

  - The dataset created using TripleX should be compatible with the training requirements of the Mochi LoRA model as described in the guide.

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
   git clone https://github.com/your-username/TripleX.git
   ```

3. **Create a New Branch**:

   ```bash
   git checkout -b feature/new-utility
   ```

4. **Make Your Changes**: Add your downloader or utility script.
5. **Commit Your Changes**:

   ```bash
   git add .
   git commit -m "Add new utility for dataset creation"
   ```

6. **Push to Your Fork**:

   ```bash
   git push origin feature/new-utility
   ```

7. **Open a Pull Request**: Go to the original repository and click "New Pull Request."

   **Note**: Be cautious about including large files (e.g., model files) in your commits. If your changes involve large files, consider alternative methods such as hosting the files externally or using Git LFS (Large File Storage).

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

## Disclaimer

- **Legal Compliance**: This toolkit is intended for educational and personal use. Users are responsible for ensuring they comply with all applicable laws, regulations, and terms of service of the websites they interact with.
- **Content Rights**: Downloading and distributing copyrighted material without permission may infringe on intellectual property rights.
- **Content Sensitivity**: Some downloaders may interact with websites containing sensitive content. Users should be aware of and comply with all legal age restrictions and content regulations in their jurisdiction.
- **No Liability**: The authors and contributors of this project are not liable for any misuse of the toolkit.

---

**Thank you for using TripleX!** If you have any questions or need assistance, feel free to open an issue on the repository or reach out to the maintainers.

---

## Additional Notes

- **Logging**: The scripts log their activities, which can be helpful for debugging.

- **Error Handling**: The scripts include basic error handling to inform you of issues that may arise during processing.

- **Dependencies**: Ensure that all dependencies listed in `requirements.txt` are installed in your virtual environment. If you encounter issues, double-check that all required packages are installed.

  ```plaintext
  # requirements.txt

  requests
  scenedetect
  beautifulsoup4
  tensorflow
  opencv-python
  numpy
  ```

- **FFmpeg**: FFmpeg is a crucial dependency for video processing in this toolkit. Ensure that it is correctly installed and accessible from your system's PATH.

- **Python Version**: This toolkit is developed for Python 3.x. Ensure you are using a compatible version of Python.

- **Model Files**: The machine learning models required for frame analysis are downloaded using `setup_models.py`. Do not add these large files directly to the repository.

### Handling Large Files

- **Git Limitations**:

  - Git repositories have file size limitations. Pushing files larger than 50 MB is generally discouraged, and files over 100 MB are rejected.

- **Using `setup_models.py`**:

  - The `setup_models.py` script handles the downloading of large model files from external sources (e.g., Google Drive) and places them in the appropriate directories.

- **Modifying `setup_models.py`**:

  - If you have new models or updates, modify `setup_models.py` to include the new download links and ensure models are placed correctly.

- **Alternative Methods**:

  - If you prefer, you can manually download the models and place them in the `models/` directory following the required structure.

### Contributing with Large Files

- **Avoid Committing Large Files**:

  - Do not commit files larger than 50 MB to the repository.

- **Use External Hosting**:

  - For large files, host them on external services like Google Drive, and modify `setup_models.py` to download them.

- **Git Large File Storage (LFS)**:

  - Alternatively, consider using Git LFS for handling large files. Note that users cloning the repository will need to have Git LFS installed.

## Contact

- **Maintainer**: NSFW API
- **Email**: nsfwapi@gmail.com
- **GitHub Issues**: Please report any issues or bugs by opening an issue on the repository.

---

Feel free to reach out if you need any further assistance or have suggestions for improving the toolkit!