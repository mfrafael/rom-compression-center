import os
from config import ROMS_FOLDER, COMPRESSIBLE_EXTENSIONS


def generate_banner():
    banner = """
.----------------------------------------------------------------------------------------------------------------.
|                                                                                                                |
|   ██████╗  ██████╗ ███╗   ███╗██████╗  ██████╗                                                                 |
|   ██╔══██╗██╔═══██╗████╗ ████║██╔══██╗██╔═══██╗                                                                |
|   ██████╔╝██║   ██║██╔████╔██║██████╔╝██║   ██║                                                                |
|   ██╔══██╗██║   ██║██║╚██╔╝██║██╔══██╗██║   ██║                                                                |
|   ██║  ██║╚██████╔╝██║ ╚═╝ ██║██████╔╝╚██████╔╝                                                                |
|   ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═════╝  ╚═════╝                                                                 |
|                                                                                                                |
|                                                                                                                |
|   ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ███╗██████╗ ██████╗ ███████╗███████╗███████╗██╗ ██████╗ ███╗   ██╗   |
|   ██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗ ████║██╔══██╗██╔══██╗██╔════╝██╔════╝██╔════╝██║██╔═══██╗████╗  ██║   |
|   ██████╔╝█████╗  ██║     ██║   ██║██╔████╔██║██████╔╝██████╔╝█████╗  ███████╗███████╗██║██║   ██║██╔██╗ ██║   |
|   ██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╔╝██║██╔═══╝ ██╔══██╗██╔══╝  ╚════██║╚════██║██║██║   ██║██║╚██╗██║   |
|   ██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚═╝ ██║██║     ██║  ██║███████╗███████║███████║██║╚██████╔╝██║ ╚████║   |
|   ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝   |
|   ██████╗ ██╗   ██╗██╗     ██╗  ██╗     ██████╗ ██████╗ ████████╗██╗███╗   ███╗██╗███████╗███████╗██████╗      |
|   ██╔══██╗██║   ██║██║     ██║ ██╔╝    ██╔═══██╗██╔══██╗╚══██╔══╝██║████╗ ████║██║╚══███╔╝██╔════╝██╔══██╗     |
|   ██████╔╝██║   ██║██║     █████╔╝     ██║   ██║██████╔╝   ██║   ██║██╔████╔██║██║  ███╔╝ █████╗  ██████╔╝     |
|   ██╔══██╗██║   ██║██║     ██╔═██╗     ██║   ██║██╔═══╝    ██║   ██║██║╚██╔╝██║██║ ███╔╝  ██╔══╝  ██╔══██╗     |
|   ██████╔╝╚██████╔╝███████╗██║  ██╗    ╚██████╔╝██║        ██║   ██║██║ ╚═╝ ██║██║███████╗███████╗██║  ██║     |
|   ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝     ╚═════╝ ╚═╝        ╚═╝   ╚═╝╚═╝     ╚═╝╚═╝╚══════╝╚══════╝╚═╝  ╚═╝     |
|                                                                                                                |
|                                           Author: Rafael Andrade                                               |
|                                                                                                                |
'----------------------------------------------------------------------------------------------------------------'
"""
    return banner

def prompt_for_folder_path():
    # Prompt the user to choose a folder path
    user_input = input(f"Enter a custom folder path or leave blank to use the default ROMs directory ({ROMS_FOLDER}):").strip()

    # If the user chooses the default ROMs directory
    if user_input.lower() == 'roms':
        # Use the default ROMs folder and prompt the user to choose a subfolder
        return select_subfolder_from_roms()
    # If the user inputs a custom folder path
    elif user_input:
        # Check if the provided path is a directory
        custom_folder = os.path.abspath(user_input)
        if os.path.isdir(custom_folder):
            return custom_folder
        else:
            # If the provided path is not a directory, display an error message
            print("Invalid folder path. Please enter a valid folder path.")
            exit()
    else:
        # Use the default ROMs folder and prompt the user to choose a subfolder
        return select_subfolder_from_roms()

def select_subfolder_from_roms():
    # List all subfolders in the ROMs folder
    roms_subfolders = [folder for folder in os.listdir(ROMS_FOLDER) if os.path.isdir(os.path.join(ROMS_FOLDER, folder))]

    # If there are no subfolders, display an error message and exit
    if not roms_subfolders:
        print("\nNo subfolders found in the default ROMs directory.")
        exit()

    print("\nAvailable subfolders in the default ROMs directory:")
    for index, folder in enumerate(roms_subfolders, start=1):
        print(f"{index}: {folder}")

    # Prompt the user to choose one of the subfolders
    folder_choice = input("\nEnter the number corresponding to the desired subfolder: ").strip()
    if folder_choice.isdigit() and 1 <= int(folder_choice) <= len(roms_subfolders):
        return os.path.join(ROMS_FOLDER, roms_subfolders[int(folder_choice) - 1])
    else:
        # If the user enters an invalid choice, display an error message and exit
        print("\nInvalid folder choice. Restarting script.")
        exit()

def confirm_action(folder_path):
    # Confirm before proceeding with the chosen folder path
    confirmation = input(f"\nRecompression will be run on '{folder_path}'. Continue? (Y/N): ").strip().lower()
    return confirmation == 'y'