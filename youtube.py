import yt_dlp
import os
import subprocess
import re
import unicodedata

# Funkcja do usuwania polskich znaków oraz przecinków z nazw plików (function removing polish characters from filenames)
def clean_file_name(text):
    # Usuwamy polskie znaki
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    # Usuwamy przecinki i inne znaki problematyczne
    text = re.sub(r'[^\w\s.-]', '', text)  # Usuwa wszystkie znaki poza literami, cyframi, spacjami i myślnikami
    text = text.replace(' ', '_')  # Zamienia spacje na podkreślenia
    return text

# Function to load data from source text file
def load_links_languages_and_fonts(file_path):
    links = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.strip():  # Pomija puste linie
                    link, lang, font = line.strip().split(',')
                    links.append((link, lang, font))
    except Exception as e:
        print(f'Error loading source text file: {e}')
    return links

# Function to rename files after downloading
def rename_files_in_directory(output_folder, lang_code):
    for file in os.listdir(output_folder):
        if file.endswith(f".{lang_code}.vtt") or file.endswith(".webm"):
            file_path = os.path.join(output_folder, file)
            new_file_name = clean_file_name(file)
            new_file_path = os.path.join(output_folder, new_file_name)
            if not os.path.exists(new_file_path):  # Sprawdzamy, czy plik już istnieje
                os.rename(file_path, new_file_path)
                print(f'Filename {file} was changed to: {new_file_name}')
            else:
                print(f'Filename {file} exists. Skipping...')

# Function to download video and VTT subtitles
def download_video_with_subtitles(url, lang_code, output_folder='downloads', archive_file='downloaded_videos.txt'):

    ydl_opts = {
        'format': 'bestvideo[height<=?1080]+bestaudio/best',  # Downloading best quality for video height equal or less than 1080px
        'writesubtitles': True,  # Downloading subtitles
        'subtitlesformat': 'vtt',  # Subtitles format VTT
        'writeautomaticsub': True,  # If there are no custom subtitles, it'll download automatically generated
        'subtitleslangs': [lang_code],  # Language code of subtitles (en, pl, es, it, de, etc.)
        'outtmpl': f'{output_folder}/%(title).200s.%(ext)s',  # Name of files
        'download_archive': archive_file,  # Archive file
        'nooverwrites': True # Do not overwrite videos if they already exist.
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f'Downlading videos and subtitles from: {url} (language: {lang_code})')
            ydl.download([url])
    except Exception as e:
        print(f'Error during downloading {url}: {e}')

# Funkcja do wbudowania napisów ASS do wideo za pomocą FFmpeg
def embed_subtitles(video_file, subtitle_file, output_file):
    if not os.path.exists(output_file):  # Sprawdzamy, czy plik już istnieje
        try:
            subprocess.run(['ffmpeg', '-i', video_file, '-vf', f"ass={subtitle_file}", '-c:a', 'copy', output_file])
            print(f'Subtitles was built-in to video: {output_file}')
        except Exception as e:
            print(f'Error during builting-in subtitles: {e}')
    else:
        print(f'File {output_file} already exist. Skipping...')

# Function to clear VTT from didascalias
def clean_vtt_file(vtt_file):
    try:
        with open(vtt_file, 'r') as file:
            content = file.read()

        # Delete ♪ and content from () and []
        content_cleaned = re.sub(r'[♪]', '', content)
        content_cleaned = re.sub(r'\(.*?\)', '', content_cleaned)
        content_cleaned = re.sub(r'\[.*?\]', '', content_cleaned)

        # Save changed VTT file
        with open(vtt_file, 'w') as file:
            file.write(content_cleaned)

        print(f'File VTT was cleared: {vtt_file}')

    except Exception as e:
        print(f'Error during clearing VTT: {e}')


# Funkcja do konwersji webm do mp4 za pomocą FFmpeg
def convert_webm_to_mp4(webm_file):
    mp4_file = webm_file.replace('.webm', '.mp4')

    if webm_file.endswith('.webm'):
        try:
            # Konwersja z webm do mp4
            result = subprocess.run(['ffmpeg', '-i', webm_file, '-c:v', 'libx264', '-crf', '23', '-preset', 'medium', mp4_file], stdout=None, stderr=None)
            if result.returncode == 0:
                print(f'File {webm_file} was converted to: {mp4_file}')
                return mp4_file
            else:
                print(f'Error during conversion {webm_file}: {result}')
                return None
        except Exception as e:
            print(f'Error during conversion {webm_file}: {e}')
            return None
    else:
        return None
    
def delete_old_file(old_video_file):
        if old_video_file.endswith('.webm'):
            print(f'Deleting sourcefile .webm: {old_video_file}')
            os.remove(old_video_file)
        else:
            return None


# Function to convert ASS subtitles with FFmpeg
def convert_vtt_to_ass(vtt_file, ass_file):
    if not os.path.exists(ass_file):  # Checking if file exist
        try:
            # Using FFmpeg to convert VTT -> ASS
            subprocess.run(['ffmpeg', '-i', vtt_file, ass_file])
            print(f'Subtitles was converted {vtt_file} to {ass_file}')
        except Exception as e:
            print(f'Error during subtitles conversion: {e}')
    else:
        print(f'File {ass_file} already exist. Skipping...')

# ASS file modification: font replacement, justifying
def add_animation_to_ass(ass_file, font_name):
    try:
        with open(ass_file, 'r') as file:
            lines = file.readlines()

        modified_lines = []
        for line in lines:
            if line.startswith("Style: Default"):
                # Listing elements
                parts = line.split(',')
                # Changing font (second element) and Alignment (18th element)
                parts[1] = font_name  # Setting font
                parts[18] = '5'  # Center-center (5 = center in both axis X and Y)
                parts[17] = '0' # no shadow
                parts[16] = '0' # no outline
                parts[15] = '0' # i forget what is that
                parts[2] = '40' # font size
                # Merging lines
                line = ','.join(parts)
                modified_lines.append(line)
            else:
                modified_lines.append(line)

        # Saving modified ASS
        with open(ass_file, 'w') as file:
            file.writelines(modified_lines)

        print(f'Subtitles in ASS file was centered and font was changed: {font_name}')
    except Exception as e:
        print(f'Error during modification ASS: {e}')

# Checking if video already exist
def video_with_subs_exists(video_file):
    
    return os.path.exists(video_file)



# Main function to download and process videos
def download_and_process_videos(file_path):
    links_languages_fonts = load_links_languages_and_fonts(file_path)

    for url, lang_code, font_name in links_languages_fonts:
        output_folder = 'downloads'

        download_video_with_subtitles(url, lang_code)
        rename_files_in_directory(output_folder, lang_code)

        video_file = None
        ass_file = None

        # Searching of downloaded files
        for file in os.listdir(output_folder):
            if file.endswith(f".{lang_code}.vtt"):
                vtt_file = os.path.join(output_folder, file)
                ass_file = vtt_file.replace(f'.{lang_code}.vtt', f'.{lang_code}.ass')
                video_file_name = vtt_file.replace(f'.{lang_code}.vtt', '')
                for ext in ['.mp4', '.webm', '.mkv']:
                    if os.path.exists(video_file_name + ext):
                        video_file = video_file_name + ext
                        break

                if video_file:
                    clean_vtt_file(vtt_file)
                    convert_vtt_to_ass(vtt_file, ass_file)
                    add_animation_to_ass(ass_file, font_name)
                    output_file = video_file.replace('.webm', '_with_subs.mp4')
                    old_video_file = video_file
                    #convert_webm_to_mp4(old_video_file)
                    embed_subtitles(video_file, ass_file, output_file)
                    video_file = output_file
                    delete_old_file(old_video_file)

        # After ending this loop, calling other script to process all videos without subtitles
    try:
        subprocess.run(['python', 'convert_all_webm.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error calling conversion script: {e}")
                    




# Text sourcefile (each link in format: video_link,language_code,font)
file_with_links = 'links_with_fonts.txt'

# Starting process
download_and_process_videos(file_with_links)


