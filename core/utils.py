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
    """
    platforms = _load_platforms()
    
    # Get full path as one string for searching
    path_lower = os.path.normpath(path).lower()
    
    # Look for platform names in the path
    for platform in platforms:
        # Search for variations of the platform name
        search_terms = [
            platform.lower(),                    # Original
            platform.lower().replace(" ", ""),   # No spaces
            platform.lower().replace(" ", "-"),  # Hyphenated
            platform.lower().replace(" ", "_")   # Underscored
        ]
        
        for term in search_terms:
            if term in path_lower:
                return platform  # Return with original casing
    
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
