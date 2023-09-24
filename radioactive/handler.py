"""
    This handler solely depends on pyradios module to communicate with our remote API
"""

import json
import sys

from pyradios import RadioBrowser
from rich.console import Console
from rich.table import Table
from zenlog import log

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
        except:
            log.critical("Something is wrong with your internet connection")
            sys.exit(1)

    def station_validator(self):
        """Validates a response from the API and takes appropriate decision"""

        # when no response from the API
        if not self.response:
            log.error("No stations found by the name")
            sys.exit(0)  # considering it as not an error

        # when multiple results found
        if len(self.response) > 1:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Station", justify="left")
            table.add_column("UUID", justify="center")
            table.add_column("Country", justify="center")
            table.add_column("Tags", justify="center")

            log.warn(
                "{} stations found by the name, select one and run with UUID instead".format(
                    len(self.response)
                )
            )

            for station in self.response:
                table.add_row(
                    station["name"],
                    station["stationuuid"],
                    station["countrycode"],
                    station["tags"],
                )

            console.print(table)
            log.info(
                "If the table does not fit into your screen, \
                \ntry to maximize the window , decrease the font by a bit and retry"
            )

            sys.exit(1)

        # when exactly one response found
        if len(self.response) == 1:
            log.info("Station found: {}".format(self.response[0]["name"].strip()))
            log.debug(json.dumps(self.response[0], indent=3))
            self.target_station = self.response[0]
            # register a valid click to increase its popularity
            self.API.click_counter(self.target_station["stationuuid"])
            # return name
            return self.response[0]["name"].strip()

    # ---------------------------- NAME -------------------------------- #
    def play_by_station_name(self, _name=None):
        """search and play a station by its name"""
        # TODO: handle exact error
        try:
            self.response = self.API.search(name=_name, name_exact=False)
            self.station_validator()
        except:
            log.error("Something went wrong. please try again.")
            sys.exit(1)

    # ------------------------------- UUID ------------------------------ #
    def play_by_station_uuid(self, _uuid):
        """search and play station by its stationuuid"""
        # TODO: handle exact error
        try:
            self.response = self.API.station_by_uuid(_uuid)
            return self.station_validator()  # should return a station name also
        except:
            log.error("Something went wrong. please try again.")
            sys.exit(1)

    # ----------------------- ------- COUNTRY -------------------------#
    def discover_by_country(self, _country_code, _limit):
        try:
            discover_result = self.API.search(countrycode=_country_code, limit=_limit)
        except Exception as e:
            # print(e)
            log.error("Something went wrong. please try again.")
            sys.exit(1)

        if len(discover_result) > 1:
            log.info("Result for country: {}".format(discover_result[0]["country"]))
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Station", justify="left")
            table.add_column("UUID", justify="center")
            table.add_column("State", justify="center")
            table.add_column("Tags", justify="center")
            table.add_column("Language", justify="center")

            for res in discover_result:
                table.add_row(
                    res["name"],
                    res["stationuuid"],
                    res["state"],
                    res["tags"],
                    res["language"],
                )
            console.print(table)
            log.info(
                "If the table does not fit into your screen, \ntry to maximize the window , decrease the font by a bit and retry"
            )

            sys.exit(0)
        else:
            log.error("No stations found for the country code, recheck it")
            sys.exit(1)

    # ------------------- by state ---------------------

    def discover_by_state(self, _state, _limit):
        try:
            discover_result = self.API.search(state=_state, limit=_limit)
        except Exception as e:
            # print(e)
            log.error("Something went wrong. please try again.")
            sys.exit(1)

        if len(discover_result) > 1:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Station", justify="left")
            table.add_column("UUID", justify="center")
            table.add_column("Country", justify="center")
            table.add_column("Tags", justify="center")
            table.add_column("Language", justify="center")

            for res in discover_result:
                table.add_row(
                    res["name"],
                    res["stationuuid"],
                    res["country"],
                    res["tags"],
                    res["language"],
                )
            console.print(table)
            log.info(
                "If the table does not fit into your screen, \ntry to maximize the window , decrease the font by a bit and retry"
            )

            sys.exit(0)
        else:
            log.error("No stations found for the state, recheck it")
            sys.exit(1)

    # -----------------by language --------------------

    def discover_by_language(self, _language, _limit):
        try:
            discover_result = self.API.search(language=_language, limit=_limit)
        except Exception as e:
            # print(e)
            log.error("Something went wrong. please try again.")
            sys.exit(1)

        if len(discover_result) > 1:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Station", justify="left")
            table.add_column("UUID", justify="center")
            table.add_column("Country", justify="center")
            table.add_column("Tags", justify="center")

            for res in discover_result:
                table.add_row(
                    res["name"], res["stationuuid"], res["country"], res["tags"]
                )
            console.print(table)
            log.info(
                "If the table does not fit into your screen, \ntry to maximize the window , decrease the font by a bit and retry"
            )

            sys.exit(0)
        else:
            log.error("No stations found for the language, recheck it")
            sys.exit(1)

    # -------------------- by tag ----------------------

    def discover_by_tag(self, _tag, _limit):
        try:
            discover_result = self.API.search(tag=_tag, limit=_limit)
        except Exception as e:
            # print(e)
            log.error("Something went wrong. please try again.")
            sys.exit(1)

        if len(discover_result) > 1:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Station", justify="left")
            table.add_column("UUID", justify="center")
            table.add_column("country", justify="center")
            table.add_column("Language", justify="center")

            for res in discover_result:
                table.add_row(
                    res["name"], res["stationuuid"], res["country"], res["language"]
                )
            console.print(table)
            log.info(
                "If the table does not fit into your screen, \
                \ntry to maximize the window , decrease the font by a bit and retry"
            )

            sys.exit(0)
        else:
            log.error("No stations found for the tag, recheck it")
            sys.exit(1)

    # ---- increase click count ------------- #
    def vote_for_uuid(self, UUID):
        try:
            result = self.API.click_counter(UUID)
            return result
        except:
            log.debug("Something went wrong during increasing click count")
