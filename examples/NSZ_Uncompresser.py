import os
import argparse
import subprocess

def decompress_nsz(folder):
    if not os.path.exists(folder):
        print(f"Error: Folder '{folder}' does not exist.")
        return
    
    # Collect all .nsz files recursively
    nsz_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(".nsz"):
                nsz_files.append(os.path.join(root, file))
    
    if not nsz_files:
        print("No NSZ files found.")
        return

    # Decompress each .nsz file
    for nsz_file in nsz_files:
        print(f"Decompressing: {nsz_file}")
        try:
            subprocess.run(["nsz", "-D", nsz_file], check=True)
            os.remove(nsz_file)
        except subprocess.CalledProcessError as e:
            print(f"Error processing {nsz_file}: {e}")
    
    print("All NSZ files processed successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Decompress all NSZ files in a folder.")
    parser.add_argument("folder", nargs="?", help="Path to the folder containing NSZ files.")
    args = parser.parse_args()
    
    if not args.folder:
        args.folder = input("Enter the folder path: ").strip()
    
    decompress_nsz(args.folder)
