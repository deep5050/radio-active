""" This module saves the current playing station information to a hidden file,
and loads the data when no arguments are provide """

import json
import os.path

from zenlog import log


class Last_station:

    """Saves the last played radio station information, when user don't provide any -S or -U
    it looks for the information.

    on every successful run, it saves the station information.
    The file it uses to store the data is a hidden file under users' home directory
    """

    def __init__(self):
        self.last_station_path = None

        self.last_station_path = os.path.join(
            os.path.expanduser("~"), ".radio-active-last-station"
        )

    def get_info(self):
        try:
            with open(self.last_station_path, "r") as f:
                last_station = json.load(f)
                return last_station
        except Exception:
            return ""

    def save_info(self, station):
        """dumps the current station information as a json file"""

        log.debug("Dumping station information")
        with open(self.last_station_path, "w") as f:
            json.dump(station, f)
