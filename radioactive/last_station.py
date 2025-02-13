""" This module saves the current playing station information to a hidden file,
and loads the data when no arguments are provided. """

import json
import os
from zenlog import log
from radioactive.default_path import default_station_file_path, handle_default_path

class Last_station:
    """Saves the last played radio station information.
    
    When the user doesn't provide any -S or -U, it looks for the information.
    On every successful run, it saves the station information.
    The file it uses to store the data is a hidden file under the user's home directory.
    """

    def __init__(self):
        handle_default_path(default_station_file_path)
        self.last_station_path = os.path.join(default_station_file_path, ".radioactive-last-station")

    def get_info(self):
        """Loads the last station information from the hidden file."""
        try:
            with open(self.last_station_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            log.warning("No last station information found or invalid JSON.")
            return None

    def save_info(self, station):
        """Saves the current station information as a JSON file."""
        log.debug("Dumping station information")
        with open(self.last_station_path, "w") as f:
            json.dump(station, f)
