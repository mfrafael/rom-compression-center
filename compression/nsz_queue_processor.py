import os
import subprocess

def process_nsz_queue(queue):
    """
    Process a list of Nintendo Switch ROMs for compression or decompression using NSZ.
    Each item in the queue should be a dict: { 'action': 'Compress'|'Uncompress', 'path': <file_path> }
    """
    for item in queue:
        action = item.get('action')
        file_path = item.get('path')
        if not file_path or not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
        if action == 'Compress' and file_path.lower().endswith('.nsp'):
            print(f"Compressing NSP: {file_path}")
            try:
                subprocess.run(["nsz", "-C", file_path], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error compressing {file_path}: {e}")
        elif action == 'Uncompress' and file_path.lower().endswith('.nsz'):
            print(f"Decompressing NSZ: {file_path}")
            try:
                subprocess.run(["nsz", "-D", file_path], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error decompressing {file_path}: {e}")
        else:
            print(f"Unsupported action or file type for: {file_path}")

if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Process a queue of Nintendo Switch ROMs for NSZ compression or decompression.")
    parser.add_argument("queue_file", help="Path to a JSON file containing the queue list.")
    args = parser.parse_args()

    if not os.path.exists(args.queue_file):
        print(f"Queue file not found: {args.queue_file}")
    else:
        with open(args.queue_file, "r", encoding="utf-8") as f:
            queue = json.load(f)
        process_nsz_queue(queue)
