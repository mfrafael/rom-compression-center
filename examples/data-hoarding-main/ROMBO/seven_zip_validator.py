import os 

# Function to check if the provided 7-Zip path is valid
def validate_7zip_path(seven_zip_path):
    return os.path.exists(seven_zip_path) and os.access(seven_zip_path, os.X_OK)

# Function to prompt the user for the 7-Zip path only if the default path is not found
def prompt_for_7zip_path():
    default_seven_zip_path = r"C:\Program Files\7-Zip\7z.exe"
    if validate_7zip_path(default_seven_zip_path):
        return default_seven_zip_path
    else:
        while True:
            seven_zip_path = input("Enter the path to the 7-Zip executable: ").strip()
            if validate_7zip_path(seven_zip_path):
                return seven_zip_path
            else:
                print("Please enter a valid 7-Zip executable path.")

# Path to the 7-Zip executable
seven_zip_path = prompt_for_7zip_path()