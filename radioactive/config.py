# load configs from a file and apply.
# If any options are given on command line it will override the configs
import configparser
import getpass
import os
import sys

from zenlog import log


## TODO: remove dead code or move to cli option for writing config file
def write_a_sample_config_file():
    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Add sections and key-value pairs
    config["AppConfig"] = {
        "loglevel": "info",
        "limit": "100",
        "sort": "votes",
        "filter": "none",
        "volume": "80",
        "filepath": "/home/{user}/recordings/radioactive/",
        "filetype": "mp3",
        "player": "ffplay",
    }

    # Get the user's home directory
    home_directory = os.path.expanduser("~")

    # Specify the file path
    file_path = os.path.join(home_directory, ".radio-active-configs.ini")

    try:
        # Write the configuration to the file
        with open(file_path, "w") as config_file:
            config.write(config_file)

        log.info(f"A sample default configuration file added at: {file_path}")

    except Exception as e:
        print(f"Error writing the configuration file: {e}")


class Configs:
    def __init__(self):
        home = os.path.expanduser("~")

        xdg_config_home = os.environ.get("XDG_CONFIG_HOME") or os.path.join(home, ".config")

        xdg_config_dirs = [xdg_config_home] + (os.environ.get("XDG_CONFIG_DIRS") or "/etc/xdg").split(":")

        self.config_paths = [
            os.path.join( home, ".radio-active-configs.ini" ),
        ] + [
            os.path.join(x, "radio-active", "configs.ini") for x in xdg_config_dirs
        ]

        self.defaults = {
            "AppConfig": {
                "loglevel": "info",
                "limit": "100",
                "sort": "votes",
                "filter": "none",
                "volume": "80",
                "filepath": "/home/{user}/recordings/radioactive/",
                "filetype": "mp3",
                "player": "ffplay",
            }
        }

    def load(self):
        self.config = configparser.ConfigParser(defaults=self.defaults)

        try:
            self.config.read(self.config_paths)
        except Exception as e:
            log.error(f"Something went wrong while parsing the config file: {e}")
            log.info("Using default configurations instead")
        finally:
            options = {}
            for section, option in self.defaults.items():
                for key, value in option.items():
                    options[key] = self.config.get(section, key, fallback=value)

            # if filepath has any placeholder, replace
            # {user} to actual user map
            options["filepath"] = options["filepath"].replace(
                "{user}", getpass.getuser()
            )

            return options

