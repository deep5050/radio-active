# load configs from a file and apply.
# If any options are given on command line it will override the configs
import configparser
import getpass
import os
import sys

from zenlog import log
from radioactive.default_path import default_appconfig_file_path, handle_default_path


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

    handle_default_path(default_appconfig_file_path)
    file_path = os.path.join(default_appconfig_file_path, ".radio-active-configs.ini")

    try:
        # Write the configuration to the file
        with open(file_path, "w") as config_file:
            config.write(config_file)

        log.info(f"A sample default configuration file added at: {file_path}")

    except Exception as e:
        print(f"Error writing the configuration file: {e}")


class Configs:
    def __init__(self):
        self.config_path = os.path.join(
            os.path.expanduser("~"), ".radio-active-configs.ini"
        )

    def load(self):
        self.config = configparser.ConfigParser()

        try:
            self.config.read(self.config_path)
            options = {}
            options["volume"] = self.config.get("AppConfig", "volume")
            options["loglevel"] = self.config.get("AppConfig", "loglevel")
            options["sort"] = self.config.get("AppConfig", "sort")
            options["filter"] = self.config.get("AppConfig", "filter")
            options["limit"] = self.config.get("AppConfig", "limit")
            options["filepath"] = self.config.get("AppConfig", "filepath")
            # if filepath has any placeholder, replace
            # {user} to actual user map
            options["filepath"] = options["filepath"].replace(
                "{user}", getpass.getuser()
            )
            options["filetype"] = self.config.get("AppConfig", "filetype")
            options["player"] = self.config.get("AppConfig", "player")

            return options

        except Exception as e:
            log.error(f"Something went wrong while parsing the config file: {e}")
            # write the example config file
            write_a_sample_config_file()
            log.info("Re-run radioative")
            sys.exit(1)
