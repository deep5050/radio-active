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
    """
    Trim a string to a maximum length and add ellipsis if needed.

    Args:
    text (str): The input text to be trimmed.
    max_length (int, optional): The maximum length of the trimmed string. Defaults to 40.

    Returns:
    str: The trimmed string, possibly with an ellipsis (...) if it was shortened.
    """
    if len(text) > max_length:
        return text[:max_length] + "..."
    else:
        return text


def print_table(response, columns, sort_by="name"):
    """
    Print the table applying the sort logic.

    Args:
    response (list): A list of data to be displayed in the table.
    columns (list): List of column specifications in the format "col_name:response_key@max_str".
    sort_by (str): The column by which to sort the table.

    Returns:
    list: The original response data.
    """

    if not response:
        log.error("No stations found")
        sys.exit(1)

    if len(response) >= 1:
        table = Table(
            show_header=True,
            header_style="magenta",
            expand=True,
            min_width=85,
            safe_box=True,
            # show_footer=True,
            # show_lines=True,
            # padding=0.1,
            # collapse_padding=True,
        )
        table.add_column("ID", justify="center")

        for col_spec in columns:
            col_name, response_key, max_str = (
                col_spec.split(":")[0],
                col_spec.split(":")[1].split("@")[0],
                int(col_spec.split("@")[1]),
            )
            table.add_column(col_name, justify="left")

        # do not need extra columns for these cases
        if sort_by not in ["name", "random"]:
            table.add_column(sort_by, justify="left")

    for i, station in enumerate(response):
        row_data = [str(i + 1)]  # for ID

        for col_spec in columns:
            col_name, response_key, max_str = (
                col_spec.split(":")[0],
                col_spec.split(":")[1].split("@")[0],
                int(col_spec.split("@")[1]),
            )
            row_data.append(
                trim_string(station.get(response_key, ""), max_length=max_str)
            )

        if sort_by not in ["name", "random"]:
            row_data.append(str(station.get(sort_by, "")))

        table.add_row(*row_data)

    console.print(table)
    # log.info(
    #     "If the table does not fit into your screen, \ntry to maximize the window, decrease the font by a bit, and retry"
    # )
    return response


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

    def get_country_code(self, name):
        self.countries = self.API.countries()
        for country in self.countries:
            if country["name"].lower() == name.lower():
                return country["iso_3166_1"]
        return None

    def validate_uuid_station(self):
        if len(self.response) == 1:
            log.debug(json.dumps(self.response[0], indent=3))
            self.target_station = self.response[0]

            # register a valid click to increase its popularity
            self.API.click_counter(self.target_station["stationuuid"])

            return self.response

    # ---------------------------- NAME -------------------------------- #
    def search_by_station_name(self, _name=None, limit=100, sort_by: str = "name"):
        """search and play a station by its name"""
        reversed = sort_by != "name"

        try:
            response = self.API.search(
                name=_name,
                name_exact=False,
                limit=limit,
                order=str(sort_by),
                reverse=reversed,
            )
            print(response)
            return print_table(
                response,
                ["Station:name@30", "Country:country@20", "Tags:tags@20"],
                sort_by=sort_by,
            )
        except Exception as e:
            log.debug("Error: {}".format(e))
            log.error("Something went wrong. please try again.")
            sys.exit(1)

    # ------------------------- UUID ------------------------ #
    def play_by_station_uuid(self, _uuid):
        """search and play station by its stationuuid"""
        try:
            self.response = self.API.station_by_uuid(_uuid)
            return self.validate_uuid_station()
        except Exception as e:
            log.debug("Error: {}".format(e))
            log.error("Something went wrong. please try again.")
            sys.exit(1)

    # -------------------------- COUNTRY ----------------------#
    def discover_by_country(self, country_code_or_name, limit, sort_by: str = "name"):
        # set reverse to false if name is is the parameter for sorting
        reversed = sort_by != "name"

        # check if it is a code or name
        if len(country_code_or_name.strip()) == 2:
            # it's a code
            log.debug("Country code '{}' provided".format(country_code_or_name))
            try:
                response = self.API.search(
                    countrycode=country_code_or_name,
                    limit=limit,
                    order=str(sort_by),
                    reverse=reversed,
                )
            except Exception as e:
                log.debug("Error: {}".format(e))
                log.error("Something went wrong. please try again.")
                sys.exit(1)
        else:
            # it's name
            log.debug("Country name '{}' provided".format(country_code_or_name))
            code = self.get_country_code(country_code_or_name)
            if code:
                try:
                    response = self.API.search(
                        countrycode=code,
                        limit=limit,
                        country_exact=True,
                        order=str(sort_by),
                        reverse=reversed,
                    )
                except Exception as e:
                    log.debug("Error: {}".format(e))
                    log.error("Something went wrong. please try again.")
                    sys.exit(1)
            else:
                log.error("Not a valid country name")
                sys.exit(1)

        # display the result
        print_table(
            response,
            [
                "Station:name@30",
                "State:state@20",
                "Tags:tags@20",
                "Language:language@20",
            ],
            sort_by=sort_by,
        )
        return response

    # ------------------- by state ---------------------

    def discover_by_state(self, state, limit, sort_by: str = "name"):
        reversed = sort_by != "name"

        try:
            response = self.API.search(
                state=state, limit=limit, order=str(sort_by), reverse=reversed
            )
        except Exception:
            log.error("Something went wrong. please try again.")
            sys.exit(1)

        return print_table(
            response,
            [
                "Station:name@30",
                "Country:country@20",
                "State:state@20",
                "Tags:tags@20",
                "Language:language@20",
            ],
            sort_by=sort_by,
        )

    # -----------------by language --------------------

    def discover_by_language(self, language, limit, sort_by: str = "name"):
        reversed = sort_by != "name"

        try:
            response = self.API.search(
                language=language, limit=limit, order=str(sort_by), reverse=reversed
            )
        except Exception as e:
            log.debug("Error: {}".format(e))
            log.error("Something went wrong. please try again.")
            sys.exit(1)

        return print_table(
            response,
            [
                "Station:name@30",
                "Country:country@20",
                "Language:language@20",
                "Tags:tags@20",
            ],
            sort_by,
        )

    # -------------------- by tag ---------------------- #
    def discover_by_tag(self, tag, limit, sort_by: str = "name"):
        reversed = sort_by != "name"

        try:
            response = self.API.search(
                tag=tag, limit=limit, order=str(sort_by), reverse=reversed
            )
        except Exception as e:
            log.debug("Error: {}".format(e))
            log.error("Something went wrong. please try again.")
            sys.exit(1)

        return print_table(
            response,
            [
                "Station:name@30",
                "Country:country@20",
                "Language:language@20",
                "Tags:tags@50",
            ],
            sort_by,
        )

    # ---- Increase click count ------------- #
    def vote_for_uuid(self, UUID):
        try:
            result = self.API.click_counter(UUID)
            return result
        except Exception as e:
            log.debug("Something went wrong during increasing click count:{}".format(e))
