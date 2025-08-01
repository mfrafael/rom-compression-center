import os
import shutil
import subprocess
import zipfile
from config import *

def generate_skip_message():
    """
    Generates a message indicating the folders that will not be compressed.
    """
    num_skip_folders = len(SKIP_THESE_FOLDERS)

    if num_skip_folders == 1:
        return f"{SKIP_THESE_FOLDERS[0]} subfolder will not be compressed."
    else:
        return f"{num_skip_folders} subfolders will not be compressed."

def extract_zip_files(directory):
    """
    Extracts .zip files in the specified directory.
    """
    zip_files = [file for file in os.listdir(directory) if file.endswith(".zip")]
    total_zip_files = len(zip_files)

    if total_zip_files == 0:
        print("\nNo .zip files found.")
        return

    print(f"Found {total_zip_files} .zip files:")
    for idx, file in enumerate(zip_files, start=1):
        print(f"\n{idx}/{total_zip_files}: {file}")
        file_path = os.path.join(directory, file)
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(os.path.splitext(file_path)[0])  # Extract to a folder with the same name as the zip file
        os.remove(file_path)

    print("\nDecompression completed.")

def compress_item(item_path, seven_zip_path, compressible_extensions=COMPRESSIBLE_EXTENSIONS):
    """
    Compresses an item (folder or file) using 7-Zip and deletes the original item if compression is successful.
    
    Parameters:
        item_path (str): The path to the item to be compressed.
        seven_zip_path (str): The path to the 7-Zip executable.
        compressible_extensions (list): List of file extensions that are compressible. Default is COMPRESSIBLE_EXTENSIONS from config.
    """
    if os.path.isdir(item_path):
        base_folder = os.path.basename(item_path)

        # Check if the folder should be skipped
        if base_folder.lower() in SKIP_THESE_FOLDERS:
            print(f"Skipping compression of '{item_path}' (Skipped folder)")
            return

        # Compress the folder
        print('\n----------------------------------------------------------------------------------------------------------------\n')
        print(f"Starting compression to .7z for '{base_folder}'")
        subprocess.run([seven_zip_path, 'a', '-mm=LZMA2', '-mx9', '-mmt', '-mmtf', '-aoa', f'{item_path}.7z', item_path])
        compressed_size = os.path.getsize(f"{item_path}.7z")
        initial_size = get_folder_size(item_path)
        compression_rate = (compressed_size / initial_size) * 100
        shutil.rmtree(item_path)
        print(f"\nCompression rate of '{item_path}.7z': {compression_rate:.2f}%")
        print('\n----------------------------------------------------------------------------------------------------------------\n')
    elif any(item_path.lower().endswith(ext) for ext in compressible_extensions):
        # Compress files with compressible extensions directly
        print(f"\nStarting compression to .7z for '{os.path.basename(item_path)}'")
        compressed_filename = os.path.splitext(item_path)[0] + '.7z'
        initial_size = os.path.getsize(item_path)
        subprocess.run([seven_zip_path, 'a', '-mm=LZMA2', '-mx9', '-mmt', '-mmtf', '-aoa', compressed_filename, item_path])
        os.remove(item_path)
        compressed_size = os.path.getsize(compressed_filename)
        compression_rate = (compressed_size / initial_size) * 100
        print(f"\nCompression rate of '{compressed_filename}': {compression_rate:.2f}%")

def get_folder_size(folder_path):
    """
    Calculates the total size of a folder.
    """
    total_size = 0
    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            total_size += os.path.getsize(file_path)
    return total_size