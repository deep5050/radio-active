import os
import shutil
from zenlog import log


def _get_xdg_config_dir():
    """Return the XDG configuration directory for radio-active."""
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config_home:
        return os.path.join(xdg_config_home, "radio-active")
    # Default to ~/.config/radio-active
    return os.path.join(os.path.expanduser("~"), ".config", "radio-active")


def _get_xdg_data_dir():
    """Return the XDG data directory for radio-active."""
    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    if xdg_data_home:
        return os.path.join(xdg_data_home, "radio-active")
    # Default to ~/.local/share/radio-active
    return os.path.join(os.path.expanduser("~"), ".local", "share", "radio-active")


def get_config_path():
    """
    Get the path to the configuration file.
    Migrates from legacy path if it exists and new path does not.
    """
    legacy_path = os.path.join(os.path.expanduser("~"), ".radio-active-configs.ini")

    config_dir = _get_xdg_config_dir()
    os.makedirs(config_dir, exist_ok=True)
    new_path = os.path.join(config_dir, "config.ini")

    if os.path.exists(legacy_path) and not os.path.exists(new_path):
        log.info(f"Migrating config file from {legacy_path} to {new_path}")
        try:
            shutil.move(legacy_path, new_path)
        except Exception as e:
            log.warning(f"Could not migrate config file: {e}")
            # If migration fails, we return new_path anyway, user might have to manually move or start fresh

    return new_path


def get_alias_path():
    """
    Get the path to the alias (favorites) file.
    Migrates from legacy path if it exists and new path does not.
    """
    legacy_path = os.path.join(os.path.expanduser("~"), ".radio-active-alias")

    config_dir = _get_xdg_config_dir()  # Aliases are user config
    os.makedirs(config_dir, exist_ok=True)
    new_path = os.path.join(config_dir, "alias_map")

    if os.path.exists(legacy_path) and not os.path.exists(new_path):
        log.info(f"Migrating alias file from {legacy_path} to {new_path}")
        try:
            shutil.move(legacy_path, new_path)
        except Exception as e:
            log.warning(f"Could not migrate alias file: {e}")

    return new_path


def get_last_station_path():
    """
    Get the path to the last played station file.
    Migrates from legacy path if it exists and new path does not.
    """
    legacy_path = os.path.join(os.path.expanduser("~"), ".radio-active-last-station")

    data_dir = _get_xdg_data_dir()  # Last station is state/data
    os.makedirs(data_dir, exist_ok=True)
    new_path = os.path.join(data_dir, "last-station")

    if os.path.exists(legacy_path) and not os.path.exists(new_path):
        log.info(f"Migrating last station file from {legacy_path} to {new_path}")
        try:
            shutil.move(legacy_path, new_path)
        except Exception as e:
            log.warning(f"Could not migrate last station file: {e}")

    return new_path
