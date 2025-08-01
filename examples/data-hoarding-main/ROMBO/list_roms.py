import os
import csv
from config import ROMS_FOLDER

def list_folders(directory):
    folders = [folder for folder in os.listdir(directory) if os.path.isdir(os.path.join(directory, folder))]
    return folders

def list_roms(directory):
    roms = []
    for root, dirs, files in os.walk(directory):
        if 'OPL' in dirs:
            dirs.remove('OPL')  # Exclude the first occurrence of 'OPL' directory
        for file in files:
            if file.endswith(('.rom', '.iso', '.7z', '.rvz', '.lnk', '.wua')):
                roms.append(os.path.join(root, file))
    return roms


def get_game_name(file_path):
    # Extracting game name from file name
    return os.path.splitext(os.path.basename(file_path))[0]

def get_platform(file_path):
    # Extracting platform from folder name
    platform_index = 3
    if 'OPL' in file_path.split(os.sep):
        platform_index += 1  # Adjust index if 'OPL' is present in the path
    platform = file_path.split(os.sep)[platform_index] if len(file_path.split(os.sep)) > platform_index else ''
    return platform


def save_to_csv(roms_list, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Platform', 'Game Name', 'File Path']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for rom in roms_list:
            writer.writerow({
                'Platform': get_platform(rom),
                'Game Name': get_game_name(rom),
                'File Path': rom
            })

# List all folders
folders = list_folders(ROMS_FOLDER)

# Display the list of folders
print("Folders in X:\\Games\\ROMs:")
for i, folder in enumerate(folders, 1):
    print(f"{i}. {folder}")

# Ask user to choose a folder or run in all folders
choice = input("Enter the number of the folder to run the script in (or 'all' for all folders): ")

if choice.lower() == 'all':
    all_roms = []
    for folder in folders:
        if folder != 'OPL':  # Exclude the 'OPL' folder
            folder_path = os.path.join(ROMS_FOLDER, folder)
            roms = list_roms(folder_path)
            all_roms.extend(roms)

    output_file_path = os.path.join(ROMS_FOLDER, 'roms_list.csv')
    save_to_csv(all_roms, output_file_path)
    print(f"ROMs list saved to: {output_file_path}")


elif choice.isdigit() and int(choice) in range(1, len(folders) + 1):
    selected_folder = folders[int(choice) - 1]
    folder_path = os.path.join(ROMS_FOLDER, selected_folder)
    roms = list_roms(folder_path)
    output_file_path = os.path.join(ROMS_FOLDER, 'roms_list.csv')
    save_to_csv(roms, output_file_path)
    print(f"ROMs list saved to: {output_file_path}")

else:
    print("Invalid choice. Please enter a valid folder number or 'all'.")
