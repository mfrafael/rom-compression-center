
####
#### Este código renomeia todos os arquivos .srt para ficarem com o mesmo nome dos arquivos .mkv na pasta onde for executado.


import os
import shutil

# Define as extensões dos arquivos de vídeo e legenda
VIDEO_EXTENSIONS = [".mkv"]
SUBTITLE_EXTENSIONS = [".srt"]

# Obtém o diretório onde o script está localizado
dir_path = os.path.dirname(os.path.realpath(__file__))

# Cria as listas para armazenar os arquivos de vídeo e legenda
video_files = []
subtitle_files = []

# Percorre todos os arquivos da pasta
for file_name in os.listdir(dir_path):
    file_path = os.path.join(dir_path, file_name)
    # Verifica se o arquivo é um vídeo ou legenda
    if os.path.isfile(file_path):
        ext = os.path.splitext(file_name)[1]
        if ext.lower() in VIDEO_EXTENSIONS:
            video_files.append(file_name)
        elif ext.lower() in SUBTITLE_EXTENSIONS:
            subtitle_files.append(file_name)

# Ordena alfabeticamente as listas de arquivos de vídeo e legenda
video_files.sort()
subtitle_files.sort()

# Renomeia os arquivos de legenda para terem os mesmos nomes dos arquivos de vídeo
for i in range(len(video_files)):
    video_file_path = os.path.join(dir_path, video_files[i])
    subtitle_file_path = os.path.join(dir_path, subtitle_files[i])
    if os.path.isfile(video_file_path) and os.path.isfile(subtitle_file_path):
        subtitle_file_new_path = os.path.join(dir_path, os.path.splitext(video_files[i])[0] + ".srt")
        shutil.move(subtitle_file_path, subtitle_file_new_path)
