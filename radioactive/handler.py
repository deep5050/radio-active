"""
    This handler solely depends on pyradios module to communicate with our remote API
"""

import datetime
import json
import sys

import requests_cache
from pyradios import RadioBrowser
from rich.console import Console
from rich.table import Table
from zenlog import log

console = Console()


def trim_string(text, max_length=40):
    if len(text) > max_length:
        return text[:max_length] + "..."
    else:
        return text


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
            expire_after = datetime.timedelta(days=3)
            session = requests_cache.CachedSession(
                cache_name="cache", backend="sqlite", expire_after=expire_after
            )
            self.API = RadioBrowser(session=session)
        except Exception as e:
            log.debug("Error: {}".format(e))
            log.critical("Something is wrong with your internet connection")
            sys.exit(1)

    def station_validator(self):
        """Validates a response from the API and takes appropriate decision"""

        # when no response from the API
        if not self.response:
            log.error("No stations found by the name")
            return []
        # TODO: remove sys exit
        # sys.exit(0)  # considering it as not an error

        # when multiple results found
        if len(self.response) > 1:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("ID", justify="center")
            table.add_column("Station", justify="left")
            table.add_column("UUID", justify="center")
            table.add_column("Country", justify="center")
            table.add_column("Tags", justify="center")

            log.warn("showing {} stations with the name!".format(len(self.response)))

            for i in range(0, len(self.response)):
                station = self.response[i]
                table.add_row(
                    str(i + 1),
                    trim_string(station["name"], max_length=30),
                    station["stationuuid"],
                    station["countrycode"],
                    trim_string(
                        station["tags"]
                    ),  # trimming tags to make the table shortrer
                )

            console.print(table)
            log.info(
                "If the table does not fit into your screen, \
                \ntry to maximize the window , decrease the font by a bit and retry"
            )
            return self.response
            # TODO: remove sys exit
            # sys.exit(0)

        # when exactly one response found
        if len(self.response) == 1:
            log.info("Station found: {}".format(self.response[0]["name"].strip()))
            log.debug(json.dumps(self.response[0], indent=3))
            self.target_station = self.response[0]
            # register a valid click to increase its popularity
            self.API.click_counter(self.target_station["stationuuid"])

            return self.response
            # return self.response[0]["name"].strip()

    # ---------------------------- NAME -------------------------------- #
    def search_by_station_name(self, _name=None, limit=100):
        """search and play a station by its name"""
        # TODO: handle exact error
        try:
            self.response = self.API.search(name=_name, name_exact=False, limit=limit)
            return self.station_validator()
        except Exception as e:
            log.debug("Error: {}".format(e))
            log.error("Something went wrong. please try again.")
            sys.exit(1)

    # ------------------------------- UUID ------------------------------ #
    def play_by_station_uuid(self, _uuid):
        """search and play station by its stationuuid"""
        # TODO: handle exact error
        try:
            self.response = self.API.station_by_uuid(_uuid)
            return self.station_validator()  # should return a station name also
        except Exception as e:
            log.debug("Error: {}".format(e))
            log.error("Something went wrong. please try again.")
            sys.exit(1)

    # ----------------------- ------- COUNTRY -------------------------#
    def discover_by_country(self, country_code, limit):
        try:
            discover_result = self.API.search(countrycode=country_code, limit=limit)
        except Exception as e:
            log.debug("Error: {}".format(e))
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
                    trim_string(res["name"], max_length=30),
                    res["stationuuid"],
                    res["state"],
                    res["tags"],
                    res["language"],
                )
            console.print(table)
            log.info(
                "If the table does not fit into your screen,\
                    \ntry to maximize the window , decrease the font by a bit and retry"
            )

            sys.exit(0)
        else:
            log.error("No stations found for the country code, recheck it")
            sys.exit(1)

    # ------------------- by state ---------------------

    def discover_by_state(self, state, limit):
        try:
            discover_result = self.API.search(state=state, limit=limit)
        except Exception:
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
                    trim_string(res["name"], max_length=30),
                    res["stationuuid"],
                    res["country"],
                    trim_string(res["tags"]),
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

    def discover_by_language(self, language, limit):
        try:
            discover_result = self.API.search(language=language, limit=limit)
        except Exception as e:
            log.debug("Error: {}".format(e))
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
                    trim_string(res["name"], max_length=30),
                    res["stationuuid"],
                    res["country"],
                    trim_string(res["tags"], max_length=40),
                )
            console.print(table)
            log.info(
                "If the table does not fit into your screen, \ntry to maximize the window, decrease the font by a bit and retry"
            )

            sys.exit(0)
        else:
            log.error("No stations found for the language, recheck it")
            sys.exit(1)

    # -------------------- by tag ---------------------- #

    def discover_by_tag(self, tag, limit):
        try:
            discover_result = self.API.search(tag=tag, limit=limit)
        except Exception as e:
            log.debug("Error: {}".format(e))
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
                    trim_string(res["name"], max_length=30),
                    res["stationuuid"],
                    res["country"],
                    res["language"],
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
        except Exception as e:
            log.debug("Something went wrong during increasing click count:{}".format(e))
