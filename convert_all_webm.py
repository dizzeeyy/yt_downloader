import os
import subprocess

# Funkcja do konwersji webm do mp4 za pomocą FFmpeg
def convert_webm_to_mp4(webm_file):
    if webm_file.endswith('.webm'):
        mp4_file = webm_file.replace('.webm', '.mp4')
    elif webm_file.endswith('.mkv'):
        mp4_file = webm_file.replace('.mkv', '.mp4')
    try:
        # Konwersja z webm do mp4 z logowaniem w czasie rzeczywistym
        process = subprocess.run(
            ['ffmpeg', '-i', webm_file, '-c:v', 'libx264', '-crf', '23', '-preset', 'medium', mp4_file],
            stdout=None,  # Umożliwia logowanie FFmpeg w terminalu
            stderr=None
        )
        
        if process.returncode == 0:
            print(f'Plik {webm_file} został przekonwertowany na {mp4_file}')
            return mp4_file
        else:
            print(f'Błąd przy konwersji pliku {webm_file}')
            return None
    except Exception as e:
        print(f'Błąd przy konwersji pliku {webm_file}: {e}')
        return None

# Funkcja do przetwarzania wszystkich plików .webm w katalogu
def convert_all_webm_in_directory(directory='downloads'):
    for file in os.listdir(directory):
        if file.endswith(('.webm', '.mkv')):
            webm_file = os.path.join(directory, file)
            print(f'Konwertowanie pliku {webm_file}...')
            convert_webm_to_mp4(webm_file)
            os.remove(webm_file)
        elif file.endswith(('.vtt', '.ass')):
            vtt_ass_file = os.path.join(directory, file)
            print(f'Sprzątam pliki z tekstami: {vtt_ass_file}.')
            os.remove(vtt_ass_file)

# Wywołanie funkcji przetwarzającej pliki .webm
if __name__ == "__main__":
    convert_all_webm_in_directory('downloads')
