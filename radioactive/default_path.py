import os
import sys
from zenlog import log

def get_xdg_paths():
    """
    Retrieve the XDG base directories with proper defaults.
    XDG_CONFIG_HOME defaults to ~/.config.
    XDG_DATA_HOME defaults to ~/.local/share.
    XDG_CACHE_HOME defaults to ~/.cache.
    """
    home = os.path.expanduser("~")
    config_home = os.getenv("XDG_CONFIG_HOME", os.path.join(home, ".config"))
    data_home = os.getenv("XDG_DATA_HOME", os.path.join(home, ".local", "share"))
    cache_home = os.getenv("XDG_CACHE_HOME", os.path.join(home, ".cache"))
    return config_home, data_home, cache_home

xdg_config_home, xdg_data_home, xdg_cache_home = get_xdg_paths()

# Data files (record and station files) remain under XDG_DATA_HOME.
default_record_file_path = os.path.join(xdg_data_home, "radioactive")
default_station_file_path = os.path.join(xdg_data_home, "radioactive")

# Configuration files now use XDG_CONFIG_HOME.
default_appconfig_file_path = os.path.join(xdg_config_home, "radioactive")

def ensure_directory(path):
    """
    Ensure the directory exists, otherwise attempt to create it.
    Exits if the directory cannot be created.
    """
    try:
        os.makedirs(path, exist_ok=True)
        log.debug(f"Directory ensured: {path}")
    except Exception as e:
        log.error(f"Could not create directory {path}: {e}")
        sys.exit(1)

def handle_default_path(default_path):
    """
    Handle default path by ensuring the directory exists.
    """
    log.debug(f"Ensuring default directory: {default_path}")
    ensure_directory(default_path)

