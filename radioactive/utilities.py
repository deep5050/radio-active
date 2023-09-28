"""Handler functions for __main__.py"""

import datetime
import os
import sys

from pick import pick
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from zenlog import log

from radioactive.last_station import Last_station
from radioactive.player import kill_background_ffplays
from radioactive.recorder import record_audio_from_url

RED_COLOR = "\033[91m"
END_COLOR = "\033[0m"


def handle_log_level(args):
    log_level = args.log_level
    if log_level in ["info", "error", "warning", "debug"]:
        log.level(log_level)
    else:
        log.warning("Correct log levels are: error,warning,info(default),debug")


def handle_record(
    target_url, curr_station_name, record_file_path, record_file, record_file_format
):
    log.info("Press 'q' to stop recording")

    # check record path
    if record_file_path and not os.path.exists(record_file_path):
        log.debug("filepath: {}".format(record_file_path))
        os.makedirs(record_file_path, exist_ok=True)

    elif not record_file_path:
        log.debug("filepath: fallback to default path")
        record_file_path = os.path.join(os.path.expanduser("~"), "Music/radioactive")
        try:
            os.makedirs(record_file_path, exist_ok=True)
        except Exception as e:
            log.debug("{}".format(e))
            sys.exit(1)

    now = datetime.datetime.now()
    month_name = now.strftime("%b").upper()
    # Format AM/PM as 'AM' or 'PM'
    am_pm = now.strftime("%p")

    formatted_date_time = now.strftime(f"%d-{month_name}-%Y@%I-%M-%S-{am_pm}")
    # formatted_date_time = now.strftime("%y-%m-%d-%H:%M:%S")

    # check file format type. currently wav and mp3 supported
    if record_file_format != ("mp3" and "wav"):
        log.debug(
            "Filetype: unknown type '{}'. falling back to mp3".format(
                record_file_format
            )
        )
        record_file_format = "mp3"

    if not record_file:
        record_file = "{}-{}".format(
            curr_station_name.strip(), formatted_date_time
        ).replace(" ", "-")

    tmp_filename = f"{record_file}.{record_file_format}"
    outfile_path = os.path.join(record_file_path, tmp_filename)

    log.info(f"Recording will be saved as: \n{outfile_path}")

    record_audio_from_url(target_url, outfile_path)


def handle_welcome_screen():
    welcome = Panel(
        """
        :radio: Play any radios around the globe right from this Terminal [yellow]:zap:[/yellow]!
        :smile: Author: Dipankar Pal
        :question: Type '--help' for more details on available commands
        :bug: Visit: https://github.com/deep5050/radio-active to submit issues
        :star: Show some love by starring the project on GitHub [red]:heart:[/red]
        :dollar: You can donate me at https://deep5050.github.io/payme/
        :x: Press Ctrl+C to quit
        """,
        title="[b]RADIOACTIVE[/b]",
        width=85,
    )
    print(welcome)


def handle_update_screen(app):
    if app.is_update_available():
        update_msg = (
            "\t[blink]An update available, run [green][italic]pip install radio-active=="
            + app.get_remote_version()
            + "[/italic][/green][/blink]\nSee the changes: https://github.com/deep5050/radio-active/blob/main/CHANGELOG.md"
        )
        update_panel = Panel(
            update_msg,
            width=85,
        )
        print(update_panel)
    else:
        log.debug("Update not available")


def handle_favorite_table(alias):
    log.info("Your favorite station list is below")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Station", justify="left")
    table.add_column("URL / UUID", justify="center")
    if len(alias.alias_map) > 0:
        for entry in alias.alias_map:
            table.add_row(entry["name"], entry["uuid_or_url"])
        print(table)
        log.info(f"Your favorite stations are saved in {alias.alias_path}")
    else:
        log.info("You have no favorite station list")


def handle_add_station(alias):
    left = input("Enter station name:")
    right = input("Enter station stream-url or radio-browser uuid:")
    if left.strip() == "" or right.strip() == "":
        log.error("Empty inputs not allowed")
        sys.exit(1)
    alias.add_entry(left, right)
    log.info("New entry: {}={} added\n".format(left, right))
    sys.exit(0)


def handle_add_to_favorite(alias, station_name, station_uuid_url):
    try:
        response = alias.add_entry(station_name, station_uuid_url)
        if not response:
            user_input = input("Enter a different name: ")
            if user_input.strip() != "":
                response = alias.add_entry(user_input.strip(), station_uuid_url)
    except Exception as e:
        log.debug("Error: {}".format(e))
        log.error("Could not add to favorite. Already in list?")


def handle_station_uuid_play(handler, station_uuid):
    log.debug("Searching API for: {}".format(station_uuid))

    handler.play_by_station_uuid(station_uuid)

    log.debug("increased click count for: {}".format(station_uuid))

    handler.vote_for_uuid(station_uuid)
    try:
        station_name = handler.target_station["name"]
        station_url = handler.target_station["url"]
    except Exception as e:
        log.debug("{}".format(e))
        log.error("Somethig went wrong")
        sys.exit(1)

    return station_name, station_url


def handle_search_stations(handler, station_name, limit):
    log.debug("Searching API for: {}".format(station_name))

    return handler.search_by_station_name(station_name, limit)
    # TODO: ask user to play using a # number of the result


def handle_station_selection_menu(handler, last_station, alias):
    # Add a selection list here. first entry must be the last played station
    # try to fetch the last played station's information
    last_station_info = {}
    try:
        last_station_info = last_station.get_info()
    except Exception as e:
        log.debug("Error: {}".format(e))
        # no last station??
        pass

    log.info("You can search for a station on internet using the --search option")
    title = "Please select a station from your favorite list:"
    station_selection_names = []
    station_selection_urls = []

    # add last played station first
    if last_station_info:
        station_selection_names.append(
            f"{last_station_info['name'].strip()} (last played station)"
        )
        try:
            station_selection_urls.append(last_station_info["stationuuid"])
        except Exception as e:
            log.debug("Error: {}".format(e))
            station_selection_urls.append(last_station_info["uuid_or_url"])

    fav_stations = alias.alias_map
    for entry in fav_stations:
        station_selection_names.append(entry["name"].strip())
        station_selection_urls.append(entry["uuid_or_url"])

    options = station_selection_names
    if len(options) == 0:
        log.info(
            f"{RED_COLOR}No stations to play. please search for a station first!{END_COLOR}"
        )
        sys.exit(0)

    _, index = pick(options, title, indicator="-->")

    # check if there is direct URL or just UUID
    station_option_url = station_selection_urls[index]
    station_name = station_selection_names[index].replace("(last played station)", "")

    if station_option_url.find("://") != -1:
        # direct URL
        station_url = station_option_url
        return station_name, station_url

    else:
        # UUID
        station_uuid = station_option_url
        return handle_station_uuid_play(handler, station_uuid)


def handle_save_last_station(last_station, station_name, station_url):
    last_station = Last_station()

    last_played_station = {}
    last_played_station["name"] = station_name
    last_played_station["uuid_or_url"] = station_url

    log.debug(f"Saving the current station: {last_played_station}")
    last_station.save_info(last_played_station)


def handle_listen_keypress(
    alias,
    target_url,
    station_name,
    station_url,
    record_file_path,
    record_file,
    record_file_format,
):
    while True:
        user_input = input("Enter a command to perform an action: ")
        if user_input == "r" or user_input == "R" or user_input == "record":
            handle_record(
                target_url,
                station_name,
                record_file_path,
                record_file,
                record_file_format,
            )
        elif user_input == "rf" or user_input == "RF" or user_input == "recordfile":
            user_input = input("Enter output filename: ")
            # try to get extension from filename
            try:
                file_name, file_ext = user_input.split(".")
            except:
                file_name = user_input
                file_ext = ""  # set default

            if user_input.strip() != "":
                handle_record(
                    target_url, station_name, record_file_path, file_name, file_ext
                )

        elif user_input == "f" or user_input == "F" or user_input == "fav":
            handle_add_to_favorite(alias, station_name, station_url)

        elif (
            user_input == "q"
            or user_input == "Q"
            or user_input == "x"
            or user_input == "quit"
        ):
            kill_background_ffplays()
            sys.exit(0)
        elif user_input == "w" or user_input == "W" or user_input == "list":
            alias.generate_map()
            handle_favorite_table(alias)

        elif (
            user_input == "h"
            or user_input == "H"
            or user_input == "?"
            or user_input == "help"
        ):
            print()
            print("q/Q/x/quit: Quit radioactive")
            print("h/H/help/?: Show this help message")
            print("r/R/record: Record a station")
            print("f/F/fav: Add station to favorite list")
            print("rf/RF/recordfile: Speficy a filename for the recording")
            print()


def handle_current_play_panel(curr_station_name=""):
    panel_station_name = Text(curr_station_name, justify="center")

    station_panel = Panel(panel_station_name, title="[blink]:radio:[/blink]", width=85)
    console = Console()
    console.print(station_panel)


def handle_user_choice_from_search_result(handler, response):
    if not response:
        log.debug("No result found!")
        sys.exit(0)
    if len(response) == 1:
        # single station found
        log.debug("Exactly one result found")

        user_input = input("Want to play this station? Y/N: ")
        if user_input == ("y" or "Y"):
            log.debug("Playing UUID from single response")
            return handle_station_uuid_play(handler, response[0]["stationuuid"])
        else:
            log.debug("Quiting")
            sys.exit(0)
    else:
        # multiple station
        log.debug("Asking for user input")

        user_input = input("Type the result ID to play: ")
        try:
            user_input = int(user_input) - 1  # because ID starts from 1
            if user_input in range(0, len(response)):
                target_response = response[user_input]
                log.debug("Selected: {}".format(target_response))
                return handle_station_uuid_play(handler, target_response["stationuuid"])
            else:
                log.error("Please enter an ID within the range")
                sys.exit(1)
        except:
            log.err("Please enter an valid ID number")
            sys.exit(1)


def handle_direct_play(alias, station_name_or_url=""):
    """Play a station directly with UUID or direct stream URL"""
    if "http" in station_name_or_url.strip():
        log.debug("Direct play: URL provided")
        # stream URL
        # call using URL with no station name N/A
        return "N/A", station_name_or_url
    else:
        log.debug("Direct play: station name provided")
        # station name from fav list
        # search for the station in fav list and return name and url

        respone = alias.search(station_name_or_url)
        if not respone:
            log.error("No station found on your favorite list with the name")
            sys.exit(1)
        else:
            log.debug("Direct play: {}".format(respone))
            return respone["name"], respone["uuid_or_url"]


def handle_play_last_station(last_station):
    station_obj = last_station.get_info()
    return station_obj["name"], station_obj["uuid_or_url"]
