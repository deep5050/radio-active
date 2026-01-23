import os
import shutil
import sys
from zenlog import log


def get_user_home():
    """
    Get the user's home directory in a cross-platform way.
    """
    return os.path.expanduser("~")


def get_base_dir():
    """
    Return the base directory for radioactive files: ~/radioactive
    This acts as the central storage for config, data, and recordings
    as per user request.
    """
    home = get_user_home()
    base_dir = os.path.join(home, "radioactive")

    try:
        os.makedirs(base_dir, exist_ok=True)
    except Exception as e:
        # If we can't create the base dir, we are in trouble,
        # but we log it and proceed (might crash later if not handled)
        log.error(f"Could not create base directory {base_dir}: {e}")

    return base_dir


def _migrate_file(legacy_path, new_path, description):
    """
    Migrate a file from legacy_path to new_path if it exists.
    """
    if os.path.exists(legacy_path) and not os.path.exists(new_path):
        log.info(f"Migrating {description} from {legacy_path} to {new_path}")
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            shutil.move(legacy_path, new_path)
        except Exception as e:
            log.warning(f"Could not migrate {description}: {e}")


def get_config_path():
    """
    Get the path to the configuration file: ~/radioactive/config.ini
    """
    base_dir = get_base_dir()
    new_path = os.path.join(base_dir, "config.ini")

    home = get_user_home()

    # 1. ~/.radio-active-configs.ini
    legacy_dot_path = os.path.join(home, ".radio-active-configs.ini")
    _migrate_file(legacy_dot_path, new_path, "config file (dotfile)")

    # 2. XDG locations (from previous attempts)
    # ~/.config/radioactive/config.ini
    xdg_path_new = os.path.join(home, ".config", "radioactive", "config.ini")
    _migrate_file(xdg_path_new, new_path, "config file (xdg-new)")

    # ~/.config/radio-active/config.ini
    xdg_path_old = os.path.join(home, ".config", "radio-active", "config.ini")
    _migrate_file(xdg_path_old, new_path, "config file (xdg-old)")

    return new_path


def get_alias_path():
    """
    Get the path to the alias (favorites) file: ~/radioactive/alias_map
    """
    base_dir = get_base_dir()
    new_path = os.path.join(base_dir, "alias_map")

    home = get_user_home()

    # 1. ~/.radio-active-alias
    legacy_dot_path = os.path.join(home, ".radio-active-alias")
    _migrate_file(legacy_dot_path, new_path, "alias file (dotfile)")

    # 2. XDG locations
    xdg_path_new = os.path.join(home, ".config", "radioactive", "alias_map")
    _migrate_file(xdg_path_new, new_path, "alias file (xdg-new)")

    xdg_path_old = os.path.join(home, ".config", "radio-active", "alias_map")
    _migrate_file(xdg_path_old, new_path, "alias file (xdg-old)")

    return new_path


def get_last_station_path():
    """
    Get the path to the last played station file: ~/radioactive/last_station
    """
    base_dir = get_base_dir()
    new_path = os.path.join(base_dir, "last_station")

    home = get_user_home()

    # 1. ~/.radio-active-last_station
    legacy_dot_path = os.path.join(home, ".radio-active-last_station")
    _migrate_file(legacy_dot_path, new_path, "last station file (dotfile)")

    # 2. XDG locations (usually in local/share, but we check config too just in case)
    xdg_data_new = os.path.join(home, ".local", "share", "radioactive", "last_station")
    _migrate_file(xdg_data_new, new_path, "last station file (xdg-new)")

    xdg_data_old = os.path.join(home, ".local", "share", "radio-active", "last_station")
    _migrate_file(xdg_data_old, new_path, "last station file (xdg-old)")

    return new_path


def get_history_path():
    """
    Get the path to the history file: ~/radioactive/history.json
    """
    base_dir = get_base_dir()
    new_path = os.path.join(base_dir, "history.json")
    return new_path


def get_recordings_path():
    """
    Get the path for recordings: ~/radioactive/recordings
    """
    base_dir = get_base_dir()
    recordings_path = os.path.join(base_dir, "recordings")

    try:
        os.makedirs(recordings_path, exist_ok=True)
    except Exception as e:
        log.error(f"Could not create recordings directory {recordings_path}: {e}")
        # Not exiting here, hoping the caller handles it or it works next time

    return recordings_path
