# TripleX by NSFW API

Welcome to the **TripleX** repository! This project provides tools for downloading videos from supported websites (such as xHamster) and from Reddit, then processing these files using utilities like scene detection, trimming, frame analysis, and dataset creation for model training.

Reddit: https://www.reddit.com/r/NSFW_API  
Discord: https://discord.gg/mjnStFuCYh

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Directory Structure](#directory-structure)
- [Installation](#installation)
  - [Environment Variables](#environment-variables)
    - [Setting Up Reddit Credentials](#setting-up-reddit-credentials)
- [Usage](#usage)
  - [Downloading Videos](#downloading-videos)
  - [Downloading from Reddit](#downloading-from-reddit)
  - [Splitting Videos by Scene](#splitting-videos-by-scene)
  - [Trimming Frames from Videos](#trimming-frames-from-videos)
  - [Analyzing Frames](#analyzing-frames)
  - [Creating Datasets for Model Training](#creating-datasets-for-model-training)
- [Contributing](#contributing)
- [License](#license)
- [Disclaimer](#disclaimer)
- [Additional Notes](#additional-notes)
- [Contact](#contact)

## Overview

**TripleX** is designed to help users download videos from supported websites and perform various processing tasks such as scene detection, trimming unwanted frames, analyzing frames using machine learning models, and creating datasets for training custom AI models. The toolkit is modular, allowing for easy addition of new downloaders and utilities.

## Features

- **Video Downloaders**: Currently supports downloading videos from xHamster and Reddit.  
- **Scene Detection**: Uses PySceneDetect to split videos into individual scenes.  
- **Frame Trimming**: Trims a specified number of frames from the beginning of videos.  
- **Frame Analysis**: Analyzes frames extracted from videos using machine learning models.  
- **Dataset Creation**: Facilitates the creation of datasets for model training.  
- **Modular Utilities**: Easily add new utilities or downloaders to extend functionality.

## Directory Structure

```plaintext
.
├── LICENSE
├── README.md
├── captioners/  
│   ├── gemini.py
│   └── open_ai.py        <--- Former get_captions.py has been moved here  
├── data
│         ├── clips
│         ├── images
│         └── videos
├── downloaders
│         ├── download_xhamster.py
|         └── reddit_downloader.py
├── guides
│         ├── fine_tuning_hunyuan_video_with_finetrainers.md
│         └── fine_tuning_mochi_with_modal.md
├── requirements.txt
├── setup_models.py
└── utils
    ├── analyze_frames.py
    ├── extract_sharpest_frame.py
    ├── split_by_scene.py
    ├── training
    │         └── hunyuan
    │             └── output_clips_to_hunyuan_dataset
    └── trim_frame_beginning.py
```

- **captioners/**: Contains scripts for captioning images and videos.
- **downloaders/**: Contains scripts for downloading videos from supported websites.
- **models/**: Directory where machine learning models will be downloaded and stored.
- **data/**: Default directory where videos and processed outputs are saved.
  - **videos/**: Contains downloaded videos.
  - **clips/**: Contains clips extracted from videos based on scene detection.
  - **images/**: Contains extracted frames and analysis results.
- **requirements.txt**: Lists the Python dependencies required for the project.
- **setup_models.py**: Script to download machine learning models from Google Drive.
- **utils/**: Contains utility scripts for processing videos.
  - **split_by_scene.py**: Splits videos into scenes.
  - **trim_frame_beginning.py**: Trims frames from the beginning of videos.
  - **extract_sharpest_frame.py**: Extracts the sharpest frame from a video.
  - **analyze_frames.py**: Analyzes frames using machine learning models.

## Installation

1. Clone the Repository:
   - `git clone https://github.com/NSFW-API/TripleX.git`
   - `cd TripleX`

2. Create a Virtual Environment:
   - `python3 -m venv venv`  
   - `source venv/bin/activate`  # On macOS/Linux  
   (On Windows: `venv\Scripts\activate`)

3. Install Dependencies:
   - `pip install -r requirements.txt`

4. Install FFmpeg:
   - macOS:     `brew install ffmpeg`
   - Ubuntu:    `sudo apt-get install ffmpeg`  
   - Windows:   Download from https://ffmpeg.org, add to PATH

5. (Optional) Install TensorFlow and Additional Dependencies for further processing:
   - `pip install tensorflow opencv-python numpy`

### Environment Variables  

If you plan to use the Reddit downloader, you’ll need Reddit API credentials. We recommend storing them in a .env file. We’ve provided an example named .env_example at the repository root:

```
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=python:[App Name]:v1.0 (by /u/[YourUsername])
```

1. Copy .env_example to .env:
   `cp .env_example .env`

2. Edit .env and fill in your Reddit credentials. See the [Setting Up Reddit Credentials](#setting-up-reddit-credentials) section for how to obtain them.

3. Ensure .env is in your .gitignore so you don’t accidentally commit secrets:
   `echo ".env" >> .gitignore`

Once .env is set up, scripts like reddit_downloader.py will load these environment variables automatically (via python-dotenv) and use them to authenticate against Reddit.

#### Setting Up Reddit Credentials

To obtain the necessary client ID and secret for Reddit:

1. Create or log into your Reddit account.  
2. Open your apps preferences page:  
   https://www.reddit.com/prefs/apps/  
3. Click “Create another app…” at the bottom of the page.  
4. Provide an “App name” → pick any descriptive name, e.g. “TripleXScraper.”  
5. Under “App type,” select “script.”  
6. Enter a short description. The “About URL” and “Redirect URL” fields can be any URL (e.g. “http://localhost/”).  
7. Click “Create app.”  
8. Once created, you’ll see something like:  
   ```name: TripleXScraper  
   personal use script: ...
   secret: ...  
   redirect uri: http://localhost/
   ```

   Copy the “personal use script” value into REDDIT_CLIENT_ID and the “secret” value into REDDIT_CLIENT_SECRET.  
   Your .env might look like this:  
   REDDIT_CLIENT_ID=abc123def456  
   REDDIT_CLIENT_SECRET=abc123def4567890abcdef12345  
   REDDIT_USER_AGENT=python:TripleXScraper:v1.0 (by /u/YourUsername)

The user agent can be any descriptive string, but Reddit recommends using the format “python:app_name:vX.Y (by /u/username).”  

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

2. **The Video** will be downloaded to `data/videos`.

   - The script automatically saves the downloaded video in the `data/videos` directory.
   - No additional input is required after providing the URL.

### Downloading from Reddit

You can download images, GIFs, or videos from any public subreddit via the reddit_downloader.py script:

1. Locate reddit_downloader.py in the “downloaders” directory.
2. Ensure you have set up your Reddit API credentials in the script or via environment variables if you need them.  
3. Ensure .env is configured
4. Run the script from the root of the repository (or wherever you keep your code), specifying which subreddits to scrape and any desired flags.

Standard usage looks like this:

```
python downloaders/reddit_downloader.py SUBREDDIT_NAME [ADDITIONAL_SUBREDDITS] [OPTIONS]
```

For example:

```
python downloaders/reddit_downloader.py TittyDrop --limit 100 --convert-gifs
```

- r/TittyDrop is the subreddit you want to scrape.  
- `--limit 100` means get up to 100 “hot” posts.  
- `--convert-gifs` automatically converts downloaded GIFs into MP4s, stored in data/videos.

Below are the main flags you can use:

- `--limit N`           : Number of posts to scrape per subreddit (default=10).  
- `--skip-images`       : Skip downloading standard image files (.jpg, .png, etc.).  
- `--skip-gifs`         : Skip downloading .gif files.  
- `--skip-videos`       : Skip downloading video files (.mp4, .webm, etc.).  
- `--convert-gifs`      : Convert any downloaded .gif to .mp4 (saved in data/videos).  
- `--skip-ingest`       : Skip creating new JSON (use existing JSON from previous runs).  
- `--skip-download`     : Skip downloading (just scrape or ingest information).  

When running without any flags, the script will:

1. Scrape the specified subreddits into JSON files located in reddit_data/.  
2. Ingest those JSON files, determining which links are images, GIFs, or videos.  
3. Download each media file into the appropriate directory:  
   - data/images for static images (jpg, png, etc.)  
   - data/gifs for raw GIF files  
   - data/videos for videos (mp4, etc.) and for GIF→MP4 conversions (if --convert-gifs is used).  

After running the script, you can find your media in the data/images or data/videos directories. You can further process them with other TripleX utilities (scene detection, trimming, dataset creation, etc.).  

### Splitting Videos by Scene

The `split_by_scene.py` script splits all videos in `data/videos` into scenes based on content detection.

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
  - The script processes all videos in `data/videos`.
  - For each video, it creates a subdirectory within `data/clips` named after the video file (without extension).
  - The split scenes are saved in the respective subdirectories.

**Notes**:

- **Content Detection Parameters**:
  - The script uses default parameters for scene detection (`threshold=15.0`, `min_scene_len=15`).
  - If you wish to adjust these parameters, you can modify the default values directly in the script.

### Trimming Frames from Videos

The `trim_frame_beginning.py` script trims a specified number of frames from the beginning of all videos in `data/videos` and its subdirectories.

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
  - The script processes all videos in `data/videos` and its subdirectories.
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
   - The scenes should be located in `data/clips`.

2. **Ensure Models are Set Up**:

   - Run `setup_models.py` as described in the [Installation](#installation) section to download and set up the required models.

3. **Run the Script**:

   ```bash
   python utils/analyze_frames.py
   ```

4. **Processing**:

   - The script processes each video in `data/clips`.
   - For each video, it extracts the sharpest frame using `extract_sharpest_frame.py`.
   - The extracted frame is analyzed using the following models:

     - **Pose Classification**: Classifies the pose in the frame.
     - **Watermark Detection**: Detects any watermarks present.
     - **Genital Detection**: Identifies regions in the frame.
     - **Penetration Detection**: Detects specific activities.

5. **Outputs**:

   - Analysis results are saved in JSON format in `data/images`.
   - The analyzed frames are also saved in `data/images`.

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

**How to Train a Video Model Using TripleX and Mochi LoRA**:
- [GitHub Gist](https://gist.github.com/NSFW-API/5f3fde1b15295cb1c747a8dee1d9d18b)
- [Civitai](https://civitai.com/articles/9966)

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

## Captioning with Gemini API

In addition to its video processing utilities, **TripleX** now includes a new captioning tool located under the `/captioners` directory. This new script – `gemini.py` – generates detailed captions for all images and videos in a specified directory. It works by processing individual frames from videos (or single images) and then composing a final, cohesive composite caption for each file. The script uses Google’s Gemini models as its backend with fallback options for reliability.

### Key Features

• Generates frame-level captions for videos using a configurable sampling rate (frames per second).  
• Supports both video files (e.g., .mp4, .mov, .avi, .webm, etc.) and image files (e.g., .jpg, .png, .heic, etc.).  
• Uses fallback Gemini models for robust caption generation in case of rate limits or resource issues.  
• Creates a composite caption that unifies the descriptions from individual frames.  
• Offers an optional rewriting step that reformats the composite caption into a concise and elegant narrative.  
• Supports parallel processing for faster captioning of video frames.  
• Optionally moves the source files and their generated caption files to a specified output directory after successful processing.

### Installation and Environment Setup

1. Ensure all dependencies are installed (listed in `requirements.txt` – additional packages used by Gemini captioner include `cv2` (OpenCV), `google-generativeai`, and `python-dotenv`).  
2. Set your Gemini API key as an environment variable. You can add the following entry to your `.env` file at the root of the repository:
  
   GEMINI_API_KEY=your_gemini_api_key_here

   This key is required to authenticate with the Gemini API. If you are not already using a `.env` file for other credentials, consider creating one and adding it to your `.gitignore`.

### Usage

Run the captioner from the command line by specifying the directory containing video and/or image files:

  python captioners/gemini.py --dir <path_to_media_directory>

The script supports additional options:

- --fps
  - Specify the frames per second at which to sample video files (default is 1 FPS).

- --max_frames  
  - (Optional) Limit the total number of video frames processed per video.

- --output_dir  
  - (Optional) If provided, once captioning succeeds the script moves the source file and the generated caption files (a JSON file with both the individual frame captions and composite caption, as well as a plain text composite caption) into the specified directory.

- --custom_prompt  
  - (Optional) A custom string with extra instructions to refine the caption detail. This prompt is applied to both the individual frame captioning and the composite caption generation.

#### Example

To caption all media files in the `media` folder at 1 FPS sampling, with a custom prompt and move completed files to `finished_captions`:

  python captioners/gemini.py --dir media --fps 1 --custom_prompt "Include specific observations about background and accessories." --output_dir finished_captions

### How It Works

1. For video files, the script reads the file via OpenCV and extracts frames at the specified interval (adjustable with the `--fps` flag). Each frame is encoded as a JPEG and sent to the Gemini API for caption generation, making use of parallel processing to speed up the workflow.  
2. For image files, it generates a caption directly for the single image.  
3. After individual captions are gathered, the tool creates a composite caption that combines the observations from each frame. It then uses a rewriting model to reframe the composite caption as a refined narrative.  
4. The final outputs are saved in the same directory as the source file (or moved to an output directory if provided) as:  
   -  A JSON file (with detailed frame-level data and the composite caption) and  
   -  A text file with the composite caption.

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