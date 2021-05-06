"""
    This handler solely depends on pyradios module to communicate with our remote API
"""

import json
import sys

from pyradios import RadioBrowser
from zenlog import log
from rich.console import Console
from rich.table import Table

console = Console()


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
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Station", justify="left")
            table.add_column("Country", justify="center")
            table.add_column("UUID", justify="center")

            log.warn("{} stations found by the name, select one and run with UUID instead".format(len(self.response)))
 
            for station in self.response:
                # data = {}
                # data["name"] = station["name"]
                # data["uuid"] = station["stationuuid"]
                # data["country"] = station["country"]
                # log.info(json.dumps(data, indent=3))
                table.add_row(station['name'], station['countrycode'], station['stationuuid'])

            console.print(table)
            sys.exit(1)

        # when exactly one response found
        if len(self.response) == 1:
            log.info("Station found: {}".format(self.response[0]["name"]))
            log.debug(json.dumps(self.response[0], indent=3))
            self.target_station = self.response[0]
            # register a valid click to increase its popularity
            self.API.click_counter(self.target_station["stationuuid"])

    def play_by_station_name(self, _name=None):
        """search and play a station by its name"""

        self.response = self.API.search(name=_name, name_exact=False)
        self.station_validator()

    def play_by_station_uuid(self, _uuid):
        """search and play station by its stationuuid"""
        self.response = self.API.station_by_uuid(_uuid)
        self.station_validator()

    def discover_by_country(self,country_code):
        pass