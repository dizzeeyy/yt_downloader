import yt_dlp
import os
import subprocess
import re
import unicodedata

# Funkcja do usuwania polskich znaków oraz przecinków z nazw plików
def clean_file_name(text):
    # Usuwamy polskie znaki
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    # Usuwamy przecinki i inne znaki problematyczne
    text = re.sub(r'[^\w\s.-]', '', text)  # Usuwa wszystkie znaki poza literami, cyframi, spacjami i myślnikami
    text = text.replace(' ', '_')  # Zamienia spacje na podkreślenia
    return text

# Funkcja do wczytania linków, języków i fontów z pliku tekstowego
def load_links_languages_and_fonts(file_path):
    links = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.strip():  # Pomija puste linie
                    link, lang, font = line.strip().split(',')
                    links.append((link, lang, font))
    except Exception as e:
        print(f'Błąd przy wczytywaniu pliku z linkami: {e}')
    return links

# Funkcja do zmiany nazw plików po pobraniu
def rename_files_in_directory(output_folder, lang_code):
    for file in os.listdir(output_folder):
        if file.endswith(f".{lang_code}.vtt") or file.endswith(".webm"):
            file_path = os.path.join(output_folder, file)
            new_file_name = clean_file_name(file)
            new_file_path = os.path.join(output_folder, new_file_name)
            if not os.path.exists(new_file_path):  # Sprawdzamy, czy plik już istnieje
                os.rename(file_path, new_file_path)
                print(f'Plik {file} został zmieniony na {new_file_name}')
            else:
                print(f'Plik {file} juz istnieje. Pomijam...')

# Funkcja do pobierania wideo i napisów VTT
def download_video_with_subtitles(url, lang_code, output_folder='downloads', archive_file='downloaded_videos.txt'):

    ydl_opts = {
        'format': 'bestvideo[height<=?1080]+bestaudio/best',  # Pobieranie najlepszej dostępnej jakości
        'writesubtitles': True,  # Pobieranie napisów
        'subtitlesformat': 'vtt',  # Pobieranie napisów w formacie VTT
        'writeautomaticsub': True,  # Pobieranie automatycznych napisów, jeśli brak ręcznych
        'subtitleslangs': [lang_code],  # Pobieranie napisów w zadanym języku
        'outtmpl': f'{output_folder}/%(title).200s.%(ext)s',  # Szablon wyjściowy bez polskich znaków i przecinków
        'download_archive': archive_file,  # Plik archiwum, aby pomijać pobrane filmy
        'nooverwrites': True # Nie nadpisuj istniejących plików
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f'Pobieranie wideo i napisów z: {url} (język: {lang_code})')
            ydl.download([url])
    except Exception as e:
        print(f'Błąd przy pobieraniu {url}: {e}')

# Funkcja do wbudowania napisów ASS do wideo za pomocą FFmpeg
def embed_subtitles(video_file, subtitle_file, output_file):
    if not os.path.exists(output_file):  # Sprawdzamy, czy plik już istnieje
        try:
            subprocess.run(['ffmpeg', '-i', video_file, '-vf', f"ass={subtitle_file}", '-c:a', 'copy', output_file])
            print(f'Napisy zostały wbudowane do pliku: {output_file}')
        except Exception as e:
            print(f'Błąd przy wbudowywaniu napisów: {e}')
    else:
        print(f'Plik {output_file} juz istnieje. Pomijam...')

# Funkcja do czyszczenia pliku VTT ze znaków muzycznych oraz didaskaliów
def clean_vtt_file(vtt_file):
    try:
        with open(vtt_file, 'r') as file:
            content = file.read()

        # Usunięcie znaków ♪ oraz zawartości w nawiasach okrągłych () i kwadratowych []
        content_cleaned = re.sub(r'[♪]', '', content)
        content_cleaned = re.sub(r'\(.*?\)', '', content_cleaned)
        content_cleaned = re.sub(r'\[.*?\]', '', content_cleaned)

        # Zapisz zmieniony plik VTT
        with open(vtt_file, 'w') as file:
            file.write(content_cleaned)

        print(f'Plik VTT został oczyszczony z niechcianych znaków: {vtt_file}')

    except Exception as e:
        print(f'Błąd podczas czyszczenia pliku VTT: {e}')


# Funkcja do konwersji webm do mp4 za pomocą FFmpeg
def convert_webm_to_mp4(webm_file):
    mp4_file = webm_file.replace('.webm', '.mp4')

    if webm_file.endswith('.webm'):
        try:
            # Konwersja z webm do mp4
            result = subprocess.run(['ffmpeg', '-i', webm_file, '-c:v', 'libx264', '-crf', '23', '-preset', 'medium', mp4_file], stdout=None, stderr=None)
            if result.returncode == 0:
                print(f'Plik {webm_file} został przekonwertowany na {mp4_file}')
                return mp4_file
            else:
                print(f'Błąd przy konwersji pliku {webm_file}: {result}')
                return None
        except Exception as e:
            print(f'Błąd przy konwersji pliku {webm_file}: {e}')
            return None
    else:
        return None
    
def delete_old_file(old_video_file):
        if old_video_file.endswith('.webm'):
            print(f'Usuwam plik źródłowy .webm: {old_video_file}')
            os.remove(old_video_file)
        else:
            return None


# Funkcja do konwersji napisów VTT do ASS za pomocą FFmpeg
def convert_vtt_to_ass(vtt_file, ass_file):
    if not os.path.exists(ass_file):  # Sprawdzamy, czy plik już istnieje
        try:
            # Użycie FFmpeg do konwersji VTT -> ASS
            subprocess.run(['ffmpeg', '-i', vtt_file, ass_file])
            print(f'Napisy zostały przekonwertowane z {vtt_file} na {ass_file}')
        except Exception as e:
            print(f'Błąd przy konwersji napisów: {e}')
    else:
        print(f'Plik {ass_file} juz istnieje. Pomijam...')

# Funkcja do modyfikacji pliku ASS: podmiana czcionki, centrowanie oraz dodanie animacji
def add_animation_to_ass(ass_file, font_name):
    try:
        with open(ass_file, 'r') as file:
            lines = file.readlines()

        modified_lines = []
        for line in lines:
            if line.startswith("Style: Default"):
                # Rozdziel linię stylu na elementy
                parts = line.split(',')
                # Podmieniamy czcionkę (drugi element) oraz Alignment (17-ty element)
                parts[1] = font_name  # Ustawiamy czcionkę
                parts[18] = '5'  # Ustawiamy centrowanie (5 = centrowanie w obu osiach)
                parts[17] = '0'
                parts[16] = '0'
                parts[15] = '0'
                parts[2] = '40'
                # Składamy linię z powrotem
                line = ','.join(parts)
                modified_lines.append(line)
            else:
                modified_lines.append(line)

        # Zapisujemy zmodyfikowany plik ASS
        with open(ass_file, 'w') as file:
            file.writelines(modified_lines)

        print(f'Napisy w pliku ASS zostały wyśrodkowane i dodano czcionkę: {font_name}')
    except Exception as e:
        print(f'Błąd przy modyfikacji pliku ASS: {e}')

# Funkcja do sprawdzania, czy plik wideo z napisami już istnieje
def video_with_subs_exists(video_file):
    # Sprawdzamy, czy plik wideo z napisami już istnieje
    return os.path.exists(video_file)



# Główna funkcja do pobierania i przetwarzania wideo
def download_and_process_videos(file_path):
    links_languages_fonts = load_links_languages_and_fonts(file_path)

    for url, lang_code, font_name in links_languages_fonts:
        output_folder = 'downloads'

        download_video_with_subtitles(url, lang_code)
        rename_files_in_directory(output_folder, lang_code)

        video_file = None
        ass_file = None

        # Szukanie pobranych plików
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

        # Po zakończeniu pętli wywołujemy drugi skrypt do konwersji plików .webm na .mp4
    try:
        subprocess.run(['python', 'convert_all_webm.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Błąd przy wywoływaniu skryptu konwersji: {e}")
                    




# Plik tekstowy z linkami, językami i fontami (każdy link w formacie: link_do_filmu,język,font)
file_with_links = 'links_with_fonts.txt'

# Uruchomienie procesu
download_and_process_videos(file_with_links)


