"""
The main handler that solely depends on pyradios module to communicate with our remote API
"""

import json
import sys

from pyradios import RadioBrowser
from zenlog import log


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
            log.warn("{} stations found by the name".format(len(self.response)))

            for station in self.response:
                data = {}
                data["name"] = station["name"]
                data["uuid"] = station["stationuuid"]
                data["country"] = station["country"]

                log.info(json.dumps(data, indent=3))

            sys.exit(0)
        if len(self.response) == 1:
            log.info("Station found: {}".format(self.response[0]["name"]))
            log.debug(json.dumps(self.response[0], indent=3))
            self.target_station = self.response[0]
            self.API.click_counter(self.target_station["stationuuid"])

    def play_by_station_name(self, _name=None):
        # print(_name)
        self.response = self.API.search(name=_name, name_exact=False)
        self.station_validator()

    def play_by_station_uuid(self, _uuid):
        # print(_uuid)
        # Pyradios by default don't let you search by uuid
        # a trick is to call click_counter(uuid) directly to get the statioon info
        is_ok = "false"
        try:
            self.target_station = self.API.click_counter(_uuid)
            log.debug(json.dumps(self.target_station, indent=3))
            is_ok = self.target_station["ok"]
        except Exception:
            log.error("Could not find the station by the UUID")
            sys.exit(0)

        log.info("Station found: {}".format(self.target_station["name"]))
        temp = self.API.search(name=self.target_station["name"], name_exact=True)
        log.debug(json.dumps(temp, indent=3))
        # againg register a valid click
        if is_ok == "false":
            res = self.API.click_counter(self.target_station["stationuuid"])
            log.debug(json.dumps(res, indent=3))
