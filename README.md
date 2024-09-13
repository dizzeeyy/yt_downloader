
# YouTube Video Downloader and WebM Converter

This project allows users to download YouTube videos, convert them from `.webm` to `.mp4`, and handle subtitles. It also avoids re-downloading videos that have already been processed.

## Prerequisites

### Python Packages
- `yt_dlp`: A tool for downloading YouTube videos.
- `ffmpeg`: A tool for media format conversion and subtitle embedding. Install it using:
  ```bash
  sudo apt install ffmpeg
  ```

You can install the required Python package with:
```bash
pip install yt-dlp
```

## Files

- **`youtube.py`**: This script handles downloading of videos, converting subtitles, and embedding them into the video.
- **`convert_all_webm.py`**: Converts downloaded `.webm` and `.mkv` files to `.mp4`.
- **`links_with_fonts.txt`**: A file where each line specifies a YouTube video URL, language code for subtitles, and an optional font for the subtitles. The format is:
  ```
  https://www.youtube.com/watch?v=<VIDEO_ID>,<LANGUAGE_CODE>,<FONT_NAME>
  ```
  Example:
  ```
  https://www.youtube.com/watch?v=BW9Fzwuf43c,en,Bebas Neue
  https://www.youtube.com/watch?v=6jQybfE2vWU,,
  ```

  If the subtitle information (language code and font) is missing (as in the second example above), the script **will not download subtitles**. Instead, it will download the video file in one of the formats: `.webm`, `.mp4`, or `.mkv`. If no subtitles are available for the video, the conversion script will handle the conversion of `.webm` or `.mkv` files to `.mp4`.

- **`downloaded_videos.txt`**: Contains a list of videos that have already been downloaded. These videos will not be downloaded again as long as their URLs remain in this file.

## Usage

### 1. Download Videos and Subtitles

First, populate the `links_with_fonts.txt` file with the videos you wish to download. Each entry should include:
- The YouTube video URL.
- A language code for subtitles (optional).
- A font name for the subtitles (optional).

To download the videos, run the `youtube.py` script:

```bash
python youtube.py
```

This script will:
- Check `downloaded_videos.txt` to avoid re-downloading already processed videos.
- Download videos and subtitles based on the `links_with_fonts.txt` file:
  - If the subtitle information is missing (e.g., `,,`), it will only download the video in `.webm`, `.mp4`, or `.mkv` format without subtitles.
- Clean and convert `.vtt` subtitle files to `.ass` format.
- Embed subtitles into the videos (if available).

### 2. Convert WebM/MKV to MP4 (automatically)

Once the videos are downloaded and don't have subtitles, it'll be converted to `.mp4` automatically after ending first script `youtube.py`. You can convert them manually from `.webm` or `.mkv` format to `.mp4` using the `convert_all_webm.py` script:

```bash
python convert_all_webm.py
```

This script will:
- Convert all `.webm` and `.mkv` files in the download directory to `.mp4` using `ffmpeg`.
- Remove unnecessary subtitle files once they have been embedded into the video.

If video has subtitles already downloaded it'll be automatically converted to `.mp4` during `youtube.py` execution.

### Example Workflow

1. Add video URLs to `links_with_fonts.txt`.
2. Run `youtube.py` to download the videos and subtitles.
3. Run `convert_all_webm.py` to convert `.webm` or `.mkv` files to `.mp4`.

## Functions Overview

### `youtube.py`
- **`download_video_with_subtitles()`**: Downloads videos from YouTube and processes subtitles.
- **`clean_vtt_file()`**: Cleans the `.vtt` subtitle files by removing unnecessary characters.
- **`convert_vtt_to_ass()`**: Converts `.vtt` subtitle files to `.ass`.
- **`embed_subtitles()`**: Embeds `.ass` subtitle files into the video.
  
### `convert_all_webm.py`
- **`convert_all_webm_in_directory()`**: Converts all `.webm` and `.mkv` files to `.mp4` using `ffmpeg`.

## License

This project is licensed under the MIT License.
