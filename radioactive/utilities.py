"""Handler functions for __main__.py"""

import datetime
import sys

from pick import pick
from rich import print
from rich.panel import Panel
from rich.table import Table
from zenlog import log

from radioactive.last_station import Last_station
from radioactive.player import Player, kill_background_ffplays
from radioactive.recorder import record_audio_from_url

RED_COLOR = "\033[91m"
END_COLOR = "\033[0m"


def handle_log_level(args):
    log_level = args.log_level
    if log_level in ["info", "error", "warning", "debug"]:
        log.level(log_level)
    else:
        log.warning("Correct log levels are: error,warning,info(default),debug")


def handle_record(target_url, curr_station_name, record_file):
    log.info("Press 'q' to stop recording")

    now = datetime.datetime.now()
    month_name = now.strftime("%b").upper()
    # Format AM/PM as 'AM' or 'PM'
    am_pm = now.strftime("%p")

    formatted_date_time = now.strftime(f"%d-{month_name}-%Y-%I-%M-{am_pm}")
    # formatted_date_time = now.strftime("%y-%m-%d-%H:%M:%S")

    if not record_file:
        record_file = "{}-{}".format(
            curr_station_name.strip(), formatted_date_time
        ).replace(" ", "-")

    log.info(f"Recording will be saved as: {record_file}.mp3")

    record_audio_from_url(target_url, f"{record_file}.mp3")


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
    station_name = handler.target_station["name"]
    station_url = handler.target_station["url"]

    return station_name, station_url


def handle_search_stations(handler, station_name, limit):
    log.debug("Searching API for: {}".format(station_name))

    handler.search_by_station_name(station_name, limit)


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

    log.info("You can search for a station on internet using the --station option")
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


def handle_listen_keypress(alias, target_url, station_name, station_url, record_file):
    while True:
        user_input = input("Enter a command to perform an action: ")
        if user_input == "r" or user_input == "R" or user_input == "record":
            handle_record(target_url, station_name, record_file)
        elif user_input == "rf" or user_input == "RF" or user_input == "recordfile":
            user_input = input("Enter output filename: ")
            if user_input.strip() != "":
                handle_record(target_url, station_name, user_input)

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
