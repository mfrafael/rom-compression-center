import os
from seven_zip_validator import seven_zip_path
from user_input_handler import prompt_for_folder_path, confirm_action, generate_banner
from folder_operations import extract_zip_files, compress_item
from config import *
from check_requirements import  check_requirements

def main():
    while True:
        # Prompt the user for the folder path
        os.system('cls')
        print(generate_banner())
        
        check_requirements("requirements.txt") # Check if all requirements are installed. If not, install them.

        root_folder = prompt_for_folder_path()

        # Confirm before proceeding
        if not confirm_action(root_folder):
            print("\nInvalid choise. Restaring script.")
            os.system('cls')
            continue  # Restart the loop so the user can start over

        # Extract .zip files in the specified folder
        extract_zip_files(root_folder)

        # Check if there are .zip files
        zip_files_found = any(item.endswith(".zip") for item in os.listdir(root_folder))

        # Check if there are files or folders to compress
        items_to_compress = [item for item in os.listdir(root_folder) if os.path.isdir(os.path.join(root_folder, item)) or any(item.lower().endswith(ext) for ext in COMPRESSIBLE_EXTENSIONS)]

        # Display appropriate messages based on the presence of .zip files and items to compress
        if not items_to_compress:
            print("No items found to process.")
            break  # End the loop if there are no items to process

        # Determine the number of subfolders to skip
        num_skip_folders = len(SKIP_THESE_FOLDERS)

        # Generate the appropriate message based on the number of subfolders
        if num_skip_folders == 1:
            skip_message = f"{SKIP_THESE_FOLDERS[0]} subfolder will not be compressed."
        else:
            skip_message = f"{num_skip_folders} subfolders will not be compressed."

        print(f"\nStarting Compression to .7z ({skip_message})")

        # Compress folders and files using 7zip, ignoring the folders specified in SKIP_THESE_FOLDERS
        for item in items_to_compress:
            item_path = os.path.join(root_folder, item)
            if os.path.isdir(item_path) and item.lower() not in SKIP_THESE_FOLDERS:
                compress_item(item_path, seven_zip_path)
            elif any(item.lower().endswith(ext) for ext in COMPRESSIBLE_EXTENSIONS):
                compress_item(item_path, seven_zip_path)

        # End the loop after processing the items
        break

if __name__ == "__main__":
    main()
