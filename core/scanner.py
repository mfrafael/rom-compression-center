from core import utils

def scan_and_prepare_roms(folder, status_label=None, progress_bar=None):
    # Busca configurações do user_config.yaml
    config_path = None
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_config.yaml"),
    ]
    for p in possible_paths:
        if os.path.exists(p):
            config_path = p
            break
    ignored = []
    ignore_textures = True
    ignore_system_files = True
    system_exts = []
    if config_path:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
            ignored = config.get("ignored_folders", [])
            ignore_textures = config.get("ignore_textures", True)
            ignore_system_files = config.get("ignore_system_files", True)
            system_exts = config.get("system_extensions", ['.ini', '.sys', '.dll', '.bat', '.tmp', '.lnk', '.dat', '.db', '.log', '.sav', '.cfg', '.bin', '.cue'])
    file_list = scan_rom_folder(folder, ignored, ignore_textures, ignore_system_files, system_exts)
    details_list = []
    for idx, file_path in enumerate(file_list):
        name = os.path.basename(file_path)
        platform = utils.get_platform_from_path(file_path)
        size = utils.get_human_size(os.path.getsize(file_path))
        action = ""
        details_list.append((name, platform, file_path, size, action))
        if status_label:
            status_label.setText(f"Processing: {name}")
        if progress_bar:
            progress_bar.setValue(idx+1)
    return details_list, file_list
import os
import yaml

def get_rom_folder():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_config.yaml")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
            return config.get("default_folder", "")
    return ""


def scan_rom_folder(folder, ignored=None, ignore_textures=True, ignore_system_files=True, system_exts=None):
    if ignored is None:
        ignored = []
    if system_exts is None:
        system_exts = ['.ini', '.sys', '.dll', '.bat', '.tmp', '.lnk', '.dat', '.db', '.log', '.sav', '.cfg', '.bin', '.cue']
    ignored = [os.path.normpath(p) for p in ignored]
    file_list = []
    for root, dirs, files in os.walk(folder):
        if ignore_textures:
            dirs[:] = [d for d in dirs if d.lower() != "textures" and os.path.normpath(os.path.join(root, d)) not in ignored]
        else:
            dirs[:] = [d for d in dirs if os.path.normpath(os.path.join(root, d)) not in ignored]
        for file in files:
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            if ignore_system_files and ext in system_exts:
                continue
            file_list.append(file_path)
    return file_list
