# ROM Recompression Script

This script is designed to automate the process of recompressing ROM files in a specified directory using 7-Zip. It allows users to choose a directory containing ROM files, extracts any .zip files found, compresses specified files and folders, and skips specified folders during compression.

## Features

- Extracts .zip files in the specified directory.
- Compresses specified files and folders using 7-Zip.
- Skips specified folders during compression.
- Allows users to choose a custom directory or use the default ROMs directory.

## Requirements

- Python 3.x
- 7-Zip installed and added to the system PATH

## Usage

1. Clone or download the repository to your local machine.

2. Install Python 3.x if you haven't already.

3. Install 7-Zip if you haven't already and make sure it's added to the system PATH.

4. Open a terminal or command prompt and navigate to the directory containing the script files.

5. Run the `main.py` script:

    ```
    python main.py
    ```

6. Follow the on-screen prompts to choose a directory and confirm the recompression action.

7. Wait for the script to finish processing the files.

## Configuration

- You can customize the behavior of the script by modifying the settings in the `config.py` file. This includes specifying compressible file extensions, compressible folders, folders to skip, and the default ROMs folder.

## Disclaimer

This script is provided as-is and may not work perfectly in all environments. Use it at your own risk and always make sure to have backups of your files before running any automated processes.