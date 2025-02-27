import argparse
import json
import os
import re
import subprocess
import time
import uuid
from urllib.parse import urlparse

import praw
import prawcore
import requests
from dotenv import load_dotenv

load_dotenv()

IMAGES_DIR = "data/images"
VIDEOS_DIR = "data/videos"
GIFS_DIR = "data/gifs"

# ------------------------------------------------------------------------------
# 1) Scrape Reddit Subreddits
# ------------------------------------------------------------------------------


def init_reddit():
    """
    Initialize and return the Reddit API connection using PRAW.
    """
    reddit = praw.Reddit(
        client_id="PfSDpPEnPWtOCiu0uUVQfA",
        client_secret="d36J9VfzeZi8GbFJltaFQKDyHhPa0A",
        user_agent="python:NSFW API:v1.0 (by /u/pornly_io)",
    )
    return reddit


def modify_reddit_url(url):
    """
    Convert preview.redd.it links to i.redd.it, remove query params.
    """
    if "https://preview.redd.it" in url:
        url = url.replace("preview.redd.it", "i.redd.it")
        url = re.sub(r"\?.*$", "", url)
    return url


def extract_urls(text):
    """
    Extract all URLs from text using a regex.
    """
    url_pattern = (
        r"https?://(?:www\.)?[-\w]+(?:\.\w[-\w]*)+[:\d]*?"
        r'(?:/[^\s"<>]*[^\s"<>.,;:!?()])?'
    )
    cleaned_text = re.sub(r"\[.*?\]\((.*?)\)", r"\1", text)
    return re.findall(url_pattern, cleaned_text)


def load_scraped_posts(tracking_file="scraped_posts.json"):
    """
    Load the set of previously scraped post IDs from a JSON file.
    Returns an empty set if the file doesn't exist.
    """
    if os.path.exists(tracking_file):
        with open(tracking_file, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_scraped_posts(post_ids, tracking_file="scraped_posts.json"):
    """
    Save the set of scraped post IDs to a JSON file.
    """
    with open(tracking_file, "w", encoding="utf-8") as f:
        json.dump(list(post_ids), f, indent=2)


def scrape_subreddits_list(
    sub_list, output_dir="reddit_data", limit=None, fresh_start=False
):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    reddit = init_reddit()
    tracking_file = "scraped_posts.json"
    scraped_ids = set() if fresh_start else load_scraped_posts(tracking_file)

    for sub_name in sub_list:
        results = []
        sub_path = os.path.join(output_dir, f"{sub_name}.json")

        try:
            print(f"\nScraping subreddit: {sub_name}")
            for submission in reddit.subreddit(sub_name).hot(limit=limit):
                if submission.id in scraped_ids:
                    print(f"  Skipping already scraped post: {submission.title}")
                    continue

                print(f"  Post: {submission.title}")
                try:
                    if (
                        hasattr(submission, "preview")
                        and "images" in submission.preview
                    ):
                        images = submission.preview["images"]
                        highest_res = max(
                            images[0]["resolutions"],
                            key=lambda x: x["width"] * x["height"],
                        )
                        image_url = highest_res["url"]
                        urls_in_text = [modify_reddit_url(image_url)]
                    else:
                        urls_in_text = [
                            modify_reddit_url(u)
                            for u in extract_urls(submission.selftext)
                        ]
                        urls_in_text.append(modify_reddit_url(submission.url))

                    results.append(
                        {
                            "submission_url": f"https://www.reddit.com/{submission.permalink}",
                            "selftext": submission.selftext,
                            "urls_in_text": urls_in_text,
                            "subreddit": sub_name,
                            "post_id": submission.id,
                        }
                    )
                    scraped_ids.add(submission.id)

                except prawcore.exceptions.TooManyRequests:
                    print("  Rate limit exceeded, sleeping 60s...")
                    time.sleep(60)
                except Exception as e:
                    print(f"  Error processing post: {submission.title} | {e}")

        except prawcore.exceptions.NotFound:
            print(f"  Subreddit not found: {sub_name}")
            continue
        except Exception as e:
            print(f"  Error scraping subreddit {sub_name}: {e}")
            continue

        if results:
            with open(sub_path, "w", encoding="utf-8") as out_f:
                json.dump(results, out_f, indent=2)
            print(f"  -> {sub_path} written.")
        else:
            print(f"  -> No data for {sub_name}.")

    save_scraped_posts(scraped_ids, tracking_file)


# ------------------------------------------------------------------------------
# 2) Identify File Types & Ingest
# ------------------------------------------------------------------------------


def get_file_extension(url):
    """Return a file extension in lowercase, e.g. '.gif' or '.jpg'"""
    parsed = urlparse(url)
    return os.path.splitext(parsed.path)[1].lower()


def get_file_type(url):
    """
    Return a string: 'image', 'gif', 'video', or 'unknown' based on extensions.
    """
    ext = get_file_extension(url)
    if ext in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
        return "image"
    elif ext == ".gif":
        return "gif"
    elif ext in [".mp4", ".webm", ".mov"]:
        return "video"
    else:
        return "unknown"


def ingest_file(json_path):
    items = []
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

        for post in data:
            submission_url = post["submission_url"]
            sub_name = post.get("subreddit", "unknown")

            for media_url in post["urls_in_text"]:
                file_type = get_file_type(media_url)

                items.append(
                    {
                        "submission_url": submission_url,
                        "subreddit": sub_name,
                        "media_url": media_url,
                        "file_type": file_type,
                    }
                )
    return items


def ingest_directory(scrape_dir="reddit_data", completed_list_file="complete.txt"):
    """
    Gather all .json files in scrape_dir and parse them with ingest_file(),
    skipping filenames listed in completed_list_file.
    """
    all_items = []

    if os.path.exists(completed_list_file):
        with open(completed_list_file, "r") as c:
            completed_files = set(c.read().splitlines())
    else:
        completed_files = set()

    for fname in sorted(os.listdir(scrape_dir)):
        if not fname.endswith(".json"):
            continue
        if fname in completed_files:
            print(f"Skipping {fname} (in completed list).")
            continue

        path = os.path.join(scrape_dir, fname)
        print(f"Ingesting: {path}")
        chunk = ingest_file(path)
        all_items.extend(chunk)

    return all_items


# ------------------------------------------------------------------------------
# 3) Download Media
# ------------------------------------------------------------------------------


def download_media(
    items, skip_images=False, skip_gifs=False, skip_videos=False, convert_gifs=False
):
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    os.makedirs(GIFS_DIR, exist_ok=True)

    for i, item in enumerate(items):
        media_url = item["media_url"]
        ftype = item["file_type"]
        subreddit_name = item.get("subreddit", "unknown")

        if ftype == "image" and skip_images:
            continue
        if ftype == "gif" and skip_gifs:
            continue
        if ftype == "video" and skip_videos:
            continue
        if ftype not in ["image", "gif", "video"]:
            continue

        try:
            resp = requests.get(media_url, timeout=10)
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {media_url}: {e}")
            continue

        parsed = urlparse(media_url)
        base_name = os.path.basename(parsed.path)

        if not base_name or "." not in base_name:
            base_name = str(uuid.uuid4()) + get_file_extension(media_url)

        prefix = f"reddit_{subreddit_name}_"
        base_name = prefix + base_name

        if ftype == "image":
            out_folder = IMAGES_DIR
        elif ftype == "video":
            out_folder = VIDEOS_DIR
        else:  # ftype == "gif"
            out_folder = GIFS_DIR

        output_path = os.path.join(out_folder, base_name)

        with open(output_path, "wb") as out_f:
            out_f.write(resp.content)

        print(f"Downloaded ({ftype.upper()}): {media_url} -> {output_path}")

        if ftype == "gif" and convert_gifs:
            mp4_name = os.path.splitext(base_name)[0] + ".mp4"
            mp4_path = os.path.join(VIDEOS_DIR, mp4_name)
            convert_gif_to_mp4(output_path, mp4_path)


# ------------------------------------------------------------------------------
# 4) Convert GIF → MP4
# ------------------------------------------------------------------------------


def convert_gif_to_mp4(input_gif, output_mp4):
    """
    Convert a .gif to .mp4 using ffmpeg.
    """
    command = [
        "ffmpeg",
        "-y",
        "-i",
        input_gif,
        "-movflags",
        "faststart",
        "-pix_fmt",
        "yuv420p",
        output_mp4,
    ]
    try:
        subprocess.run(
            command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        print(f"Converted: {input_gif} -> {output_mp4}")
    except subprocess.CalledProcessError as e:
        print(
            f"Error converting {input_gif}: {e.stderr.decode('utf-8', errors='replace')}"
        )


# ------------------------------------------------------------------------------
# 5) Main CLI
# ------------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Scrape subreddits, download images/gifs/videos, optional .gif->.mp4 conversion."
    )
    parser.add_argument(
        "subreddits", nargs="+", help="One or more subreddit names to scrape."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of hot posts to scrape per subreddit (default=10).",
    )
    parser.add_argument(
        "--skip-images",
        action="store_true",
        help="Skip downloading any image files (.jpg, .png...).",
    )
    parser.add_argument(
        "--skip-gifs", action="store_true", help="Skip downloading .gif files."
    )
    parser.add_argument(
        "--skip-videos",
        action="store_true",
        help="Skip downloading any non-gif videos (.mp4, .webm, .mov...).",
    )
    parser.add_argument(
        "--convert-gifs",
        action="store_true",
        help="Convert downloaded .gif files to .mp4 (stored in data/videos).",
    )
    parser.add_argument(
        "--skip-ingest",
        action="store_true",
        help="Skip ingest step (use existing JSON files in reddit_data/).",
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Skip download step (useful if you only wanted to scrape).",
    )
    parser.add_argument(
        "--fresh-start",
        action="store_true",
        help="Ignore previously scraped posts and start fresh.",
    )
    args = parser.parse_args()

    if not args.skip_ingest:
        scrape_subreddits_list(
            sub_list=args.subreddits,
            output_dir="reddit_data",
            limit=args.limit,
            fresh_start=args.fresh_start,
        )

    all_items = []
    if not args.skip_ingest:
        all_items = ingest_directory("reddit_data", completed_list_file="complete.txt")
    else:
        all_items = ingest_directory("reddit_data", completed_list_file="complete.txt")

    if not args.skip_download and all_items:
        download_media(
            items=all_items,
            skip_images=args.skip_images,
            skip_gifs=args.skip_gifs,
            skip_videos=args.skip_videos,
            convert_gifs=args.convert_gifs,
        )


if __name__ == "__main__":
    main()
