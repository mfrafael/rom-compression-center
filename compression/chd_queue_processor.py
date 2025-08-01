import os
import subprocess

def process_chd_queue(queue):
    """
    Process a list of ROMs for compression to CHD format using chdman.
    Each item in the queue should be a dict: { 'action': 'Compress'/'Uncompress', 'platform': <platform>, 'path': <file_path> }
    Supported platforms: Arcade (MAME), PS1, PS2, Saturn, Sega CD, Neo Geo CD, Dreamcast, TurboGrafx-CD, CD-i, 3DO
    """
    for item in queue:
        action = item.get('action')
        platform = item.get('platform')
        file_path = item.get('path')
        
        if not action or action not in ['Compress', 'Uncompress'] or not file_path or not os.path.exists(file_path):
            print(f"Skipping invalid item: {item}")
            continue
            
        # Get the chdman executable path
        chdman_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chdman", "chdman.exe")
        if not os.path.exists(chdman_path):
            print(f"ERROR: chdman.exe not found at: {chdman_path}")
            return
        
        # Handle decompression (CHD to ISO/BIN+CUE)
        if action == 'Uncompress' and file_path.lower().endswith('.chd'):
            # Para PlayStation 2, usamos bin/cue ao invés de ISO
            is_ps2 = platform and ('playstation 2' in platform.lower() or platform.lower() == 'ps2')
            
            if is_ps2:
                # Para PS2, extraímos para formato BIN/CUE
                base_name = os.path.splitext(file_path)[0]
                cue_path = base_name + '.cue'
                bin_path = base_name + '.bin'
                
                print(f"Decompressing PS2 CHD: {file_path} -> BIN/CUE format")
                
                try:
                    cmd = [chdman_path, "extractcd", "-i", file_path, "-o", cue_path, "-ob", bin_path]
                    print(f"Running command: {' '.join(cmd)}")
                    subprocess.run(cmd, check=True)
                    
                    # Verifica se os arquivos foram gerados com sucesso
                    if os.path.exists(cue_path) and os.path.exists(bin_path):
                        bin_size = os.path.getsize(bin_path)
                        cue_size = os.path.getsize(cue_path)
                        print(f"Successfully extracted {file_path} to BIN/CUE format")
                        print(f"BIN file: {bin_path} (Size: {bin_size} bytes)")
                        print(f"CUE file: {cue_path} (Size: {cue_size} bytes)")
                    else:
                        print(f"Warning: Output files not found after extraction")
                except subprocess.CalledProcessError as e:
                    print(f"Error decompressing {file_path}: {e}")
                except Exception as e:
                    print(f"General error during decompression: {e}")
            else:
                # Para outros sistemas, mantém o formato ISO
                out_path = os.path.splitext(file_path)[0] + '.iso'
                
                print(f"Decompressing CHD: {file_path} ({platform}) -> {out_path}")
                
                try:
                    cmd = [chdman_path, "extractcd", "-i", file_path, "-o", out_path]
                    print(f"Running command: {' '.join(cmd)}")
                    subprocess.run(cmd, check=True)
                    
                    # Verifica se o arquivo ISO foi gerado com sucesso
                    if os.path.exists(out_path):
                        iso_size = os.path.getsize(out_path)
                        print(f"Successfully extracted {file_path} to {out_path} (Size: {iso_size} bytes)")
                    else:
                        print(f"Warning: Output file {out_path} not found after extraction")
                except subprocess.CalledProcessError as e:
                    print(f"Error decompressing {file_path}: {e}")
                except Exception as e:
                    print(f"General error during decompression: {e}")
            continue
        
        # Handle compression
        ext = os.path.splitext(file_path)[1].lower()
        out_path = os.path.splitext(file_path)[0] + '.chd'
        print(f"Compressing to CHD: {file_path} ({platform}) -> {out_path}")
        
        # Para PlayStation 2, verificamos especialmente se é um arquivo .cue ou .bin
        is_ps2 = platform and ('playstation 2' in platform.lower() or platform.lower() == 'ps2')
        
        try:
            if is_ps2 and ext == '.cue':
                # Para PS2 com arquivo .cue, usamos o createcd do chdman
                print(f"Detected PS2 .cue file, using createcd...")
                cmd = [chdman_path, "createcd", "-i", file_path, "-o", out_path]
            elif is_ps2 and ext == '.bin':
                # Para PS2 com apenas .bin, precisamos procurar um .cue correspondente
                cue_path = os.path.splitext(file_path)[0] + '.cue'
                if os.path.exists(cue_path):
                    print(f"Found matching .cue file for PS2 .bin, using that instead: {cue_path}")
                    cmd = [chdman_path, "createcd", "-i", cue_path, "-o", out_path]
                else:
                    print(f"Warning: PS2 .bin file without .cue. Creating .cue file...")
                    # Cria um arquivo .cue básico
                    bin_name = os.path.basename(file_path)
                    with open(cue_path, 'w') as f:
                        f.write(f'FILE "{bin_name}" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00')
                    cmd = [chdman_path, "createcd", "-i", cue_path, "-o", out_path]
            elif is_ps2 and ext == '.iso':
                print(f"Warning: PS2 .iso files might not compress correctly with chdman.")
                print(f"Consider converting to .bin/.cue format first.")
                cmd = [chdman_path, "createcd", "-i", file_path, "-o", out_path]
            # Para outros formatos, mantém o comportamento atual
            elif ext in ['.cue', '.gdi', '.iso']:
                cmd = [chdman_path, "createcd", "-i", file_path, "-o", out_path]
            elif ext in ['.bin', '.img', '.raw', '.wav']:
                # Para .bin de outros sistemas, verifica se existe um .cue correspondente
                cue_path = os.path.splitext(file_path)[0] + '.cue'
                if os.path.exists(cue_path):
                    print(f"Found matching .cue file, using that instead: {cue_path}")
                    cmd = [chdman_path, "createcd", "-i", cue_path, "-o", out_path]
                else:
                    cmd = [chdman_path, "createraw", "-i", file_path, "-o", out_path]
            else:
                print(f"Unsupported file type for CHD: {file_path}")
                continue
                
            print(f"Running command: {' '.join(cmd)}")
            # Don't use shell=True to avoid path quoting issues
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error compressing {file_path} to CHD: {e}")
        except Exception as e:
            print(f"General error: {e}")

if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Process a queue of ROMs for CHD compression.")
    parser.add_argument("queue_file", help="Path to a JSON file containing the queue list.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
    args = parser.parse_args()

    if not os.path.exists(args.queue_file):
        print(f"Queue file not found: {args.queue_file}")
    else:
        with open(args.queue_file, "r", encoding="utf-8") as f:
            queue = json.load(f)
        if args.verbose:
            print("[CHD Processor] Verbose mode enabled.")
        process_chd_queue(queue)
