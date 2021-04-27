import sys
import signal
from zenlog import log
from player import Player
from pyradios import RadioBrowser


class Handler:
    def __init__(self):
        self.API = None
        self.response = None
        self.target_station = None

        self.API = RadioBrowser()

    def station_validator(self):
        if len(self.response) == 0:
            log.error("No stations found by the name")
            sys.exit(0)
        if len(self.response) > 1:
            log.info("Multiple stations found by the name")
            stations_name = ""
            for station in self.response:
                # stations_name = stations_name + "," + station["name"]
                log.info(
                    "name: {} | id: {} | country: {}".format(
                        station["name"], station["stationuuid"], station["country"]
                    )
                )

            log.info(stations_name)
            sys.exit(0)
        if len(self.response) == 1:
            log.info("Station found: {}".format(self.response[0]["name"]))
            log.debug(self.response[0])
            self.target_station = self.response[0]
            self.API.click_counter(self.target_station["stationuuid"])

    def play_by_station_name(self, _name=None):
        print(_name)
        self.response = self.API.search(name=_name, name_exact=False)
        self.station_validator()

    def play_by_station_uuid(self, _uuid):
        print(_uuid)
        # Pyradios by default don't let you search by uuid
        # a trick is to call click_counter(uuid) directly to get the statioon info
        is_ok = "false"
        try:
            self.target_station = self.API.click_counter(_uuid)
            log.debug(self.target_station)
            is_ok = self.target_station["ok"]
        except Exception as e:
            log.error("Could not find a station by the UUID")
            sys.exit(0)

        self.API.search(name=self.target_station["name"], name_exact=True)
        # againg register a valid click
        if is_ok == "false":
            res = self.API.click_counter(self.target_station["stationuuid"])
            log.debug(res)
