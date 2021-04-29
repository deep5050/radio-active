import os.path
import json
from zenlog import log


class Last_station:
    def __init__(self):
        self.last_station_path = None

        self.last_station_path = os.path.join(
            os.path.expanduser("~"), ".radio-active-last-station.json"
        )

    def get_info(self):
        try:
            with open(self.last_station_path, "r") as f:
                last_station = json.load(f)
                log.info("Playing last station: {}".format(last_station["name"]))
                return last_station["stationuuid"]
        except Exception as e:
            log.critical("Need a station name  or UUID to play the radio, see help")
            sys.exit(0)

    def save_info(self, station):
        log.debug("Dumping station information")
        with open(self.last_station_path, "w") as f:
            json.dump(station, f)
