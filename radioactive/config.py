# load configs from a file and apply.
# If any options are given on command line it will override the configs
import configparser
import getpass
import os
import sys

from zenlog import log


def write_a_sample_config_file():
    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Add sections and key-value pairs
    config["AppConfig"] = {
        "loglevel": "info",
        "limit": "100",
        "sort": "votes",
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
            log.error("Something went wrong while parsing the config file: {e}")
            # write the example config file
            write_a_sample_config_file()
            log.info("Re-run radioactive")
            sys.exit(1)
