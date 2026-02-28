import json
import os

from zenlog import log

from radioactive.paths import get_history_path


class History:
    def __init__(self):
        self.history_path = get_history_path()
        self.history_list = []
        self.load()

    def load(self):
        try:
            if os.path.exists(self.history_path):
                with open(self.history_path, "r") as f:
                    self.history_list = json.load(f)
            else:
                self.history_list = []
        except Exception as e:
            log.debug(f"Error loading history: {e}")
            self.history_list = []

    def append(self, station):
        """
        Add a station to history.
        station: dict with name, uuid, url keys mostly
        """
        # remove existing entry with same name or uuid to avoid duplicates
        # and bring it to top
        new_list = []
        for s in self.history_list:
            # check name
            if s.get("name") == station.get("name"):
                continue
            # check uuid if available
            if (
                s.get("stationuuid")
                and station.get("stationuuid")
                and s.get("stationuuid") == station.get("stationuuid")
            ):
                continue
            # check url if available (for direct play)
            if (
                s.get("url")
                and station.get("url")
                and s.get("url") == station.get("url")
            ):
                continue

            new_list.append(s)

        self.history_list = new_list
        self.history_list.insert(0, station)

        # keep only last 20
        if len(self.history_list) > 20:
            self.history_list = self.history_list[:20]

        self.save()

    def save(self):
        try:
            with open(self.history_path, "w") as f:
                json.dump(self.history_list, f, indent=4)
        except Exception as e:
            log.warning(f"Could not save history: {e}")

    def get_list(self):
        return self.history_list
