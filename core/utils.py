import os

# Cache for platforms list
_PLATFORMS = None

def _load_platforms():
    """Load and cache platform list from file."""
    global _PLATFORMS
    if _PLATFORMS is not None:
        return _PLATFORMS

    platforms_file = os.path.join(os.path.dirname(__file__), "platform_list.txt")
    try:
        with open(platforms_file, encoding="utf-8") as f:
            _PLATFORMS = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        _PLATFORMS = ["Nintendo Switch", "PlayStation", "Xbox", "PC"]  # Default platforms
    return _PLATFORMS

def get_platform_from_path(path, platforms_file=None):
    """
    Get platform from file path by checking if any part of the path matches known platforms.
    The matching is case-insensitive.
    Prefers longer matches to handle cases like "Playstation" vs "Playstation 2".
    """
    platforms = _load_platforms()
    
    # Get full path as one string for searching
    path_lower = os.path.normpath(path).lower()
    
    # Special case for Xbox 360 vs Xbox
    if "xbox 360" in path_lower or "xbox360" in path_lower or "x360" in path_lower:
        for platform in platforms:
            if platform.lower() == "microsoft xbox 360":
                return platform
    
    # Track all matches and their lengths to find the most specific one
    matches = []
    
    # Define common aliases for platforms
    platform_aliases = {
        "Sony Playstation": ["ps", "ps1", "psx", "psone"],
        "Sony Playstation 2": ["ps2", "playstation2"],
        "Sony Playstation 3": ["ps3", "playstation3"],
        "Sony Playstation 4": ["ps4", "playstation4"],
        "Nintendo Switch": ["switch", "nx"],
        "Nintendo Game Boy Advance": ["gba"],
        "Nintendo Game Boy Color": ["gbc"],
        "Nintendo GameCube": ["gc", "gamecube", "ngc"],
        "Nintendo NES": ["famicom"],
        "Nintendo SNES": ["superfamicom", "sfc"],
        "Nintendo 64": ["n64"],
        "Nintendo DS": ["nds"],
        "Nintendo 3DS": ["3ds"],
        "Nintendo Wii": ["wii"],
        "Nintendo Wii U": ["wiiu"],
        "Microsoft Xbox": ["xbox", "msxbox"],
        "Microsoft Xbox 360": ["xbox360", "x360"],
        "Sega Genesis": ["megadrive", "genesis"],
        "Sega Saturn": ["saturn"],
        "Sega Dreamcast": ["dc", "dreamcast"],
    }
    
    # Sort platforms by length in descending order to prioritize more specific names
    sorted_platforms = sorted(platforms, key=len, reverse=True)
    
    # Look for platform names in the path
    for platform in sorted_platforms:
        # Search for variations of the platform name
        search_terms = [
            platform.lower(),                    # Original
            platform.lower().replace(" ", ""),   # No spaces
            platform.lower().replace(" ", "-"),  # Hyphenated
            platform.lower().replace(" ", "_")   # Underscored
        ]
        
        # Add any aliases for this platform
        if platform in platform_aliases:
            search_terms.extend(platform_aliases[platform])
        
        for term in search_terms:
            if term in path_lower:
                # Weigh matches by term length and exact match status
                # Give preference to exact matches (entire words)
                exact_match = False
                # Check if term is a separate word or folder name
                parts = [p.lower() for p in path_lower.replace('\\', '/').split('/')]
                if term in parts:  # Exact folder name match
                    exact_match = True
                else:  # Check for exact word match with word boundaries
                    for part in parts:
                        if part == term or part.startswith(f"{term}_") or part.endswith(f"_{term}"):
                            exact_match = True
                            break
                
                # Special higher weighting for:
                # 1. Platforms that include numbers (like "Xbox 360" vs "Xbox")
                # 2. Exact matches
                # 3. Term length (longer terms are likely more specific)
                has_number = any(char.isdigit() for char in platform)
                number_bonus = 10 if has_number and any(char.isdigit() for char in term) else 0
                exact_bonus = 5 if exact_match else 0
                
                # Calculate final weight
                weight = len(term) + number_bonus + exact_bonus
                matches.append((platform, weight, term))
    
    # Return the highest weighted match or "Unknown" if no matches
    if matches:
        # Sort by weight (descending)
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[0][0]  # Return the platform name with original casing
    
    return "Unknown"


def get_human_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.2f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/1024**2:.2f} MB"
    else:
        return f"{size_bytes/1024**3:.2f} GB"


def parse_size(size_str):
    size_str = str(size_str).strip()
    if size_str.endswith('GB'):
        return float(size_str[:-2]) * 1024**3
    elif size_str.endswith('MB'):
        return float(size_str[:-2]) * 1024**2
    elif size_str.endswith('KB'):
        return float(size_str[:-2]) * 1024
    elif size_str.endswith('B'):
        return float(size_str[:-1])
    return 0
