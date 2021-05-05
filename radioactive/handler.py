"""
    This handler solely depends on pyradios module to communicate with our remote API
"""
import json
import sys

from pyradios import RadioBrowser
from zenlog import log


class Handler:
    """
    radio-browser API handler. This module communicates with the underlying API via PyRadios
    """

    def __init__(self):
        self.API = None
        self.response = None
        self.target_station = None

        # When RadioBrowser can not be initiated properly due to no internet (probably)
        try:
            self.API = RadioBrowser()
        except IndexError as e:
            log.critical("Something wrong with your internet connection")
            log.debug(e)
            sys.exit(1)

    def station_validator(self):
        """Validate a response from the API and takes appropriate decision"""

        # when no response from the API
        if not self.response:
            log.error("No stations found by the name")
            sys.exit(1)

        # when multiple results found
        if len(self.response) > 1:
            log.warn("{} stations found by the name".format(len(self.response)))

            for station in self.response:
                data = {}
                data["name"] = station["name"]
                data["uuid"] = station["stationuuid"]
                data["country"] = station["country"]
                log.info(json.dumps(data, indent=3))
            sys.exit(1)

        # when exactly one response found
        if len(self.response) == 1:
            log.info("Station found: {}".format(self.response[0]["name"]))
            log.debug(json.dumps(self.response[0], indent=3))
            self.target_station = self.response[0]
            self.API.click_counter(self.target_station["stationuuid"])

    def play_by_station_name(self, _name=None):
        """search and play a station by its name"""

        self.response = self.API.search(name=_name, name_exact=False)
        self.station_validator()

    def play_by_station_uuid(self, _uuid):
        """search and play station by its stationuuid"""

        # Pyradios by default don't let you search by uuid
        # a trick is to call click_counter(uuid) directly to get the station info
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

        # register a valid click against the current response
        if is_ok == "false":
            res = self.API.click_counter(self.target_station["stationuuid"])
            log.debug(json.dumps(res, indent=3))
