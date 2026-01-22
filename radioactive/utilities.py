"""
Handler functions for __main__.py.
Acts as a controller/orchestrator, delegating to UI and Actions modules.
"""

import sys
from random import randint
from typing import Any, Dict, List, Optional, Tuple, Union

from pick import pick
from zenlog import log

# Re-export functions for backward compatibility and aggregation
from radioactive.ui import (
    handle_welcome_screen,
    handle_update_screen,
    handle_favorite_table,
    handle_show_station_info,
    handle_current_play_panel,
    set_global_station_info,
    global_current_station_info,
)

from radioactive.actions import (
    handle_fetch_song_title,
    handle_record,
    handle_add_station,
    handle_add_to_favorite,
    handle_save_last_station,
    check_sort_by_parameter,
    handle_search_stations,
    handle_station_uuid_play,
    handle_direct_play,
    handle_play_last_station,
    handle_get_station_name_from_metadata,
    handle_station_name_from_headers,
    handle_play_random_station,
)
from radioactive.ffplay import kill_background_ffplays


RED_COLOR = "\033[91m"
END_COLOR = "\033[0m"


def handle_station_selection_menu(handler, last_station, alias) -> Tuple[str, str]:
    """
    Show a selection menu for favorite stations.
    """
    # Add a selection list here. first entry must be the last played station
    # try to fetch the last played station's information
    last_station_info = {}
    try:
        last_station_info = last_station.get_info()
    except Exception as e:
        log.debug(f"Error: {e}")
        # no last station??
        pass

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
            log.debug(f"Error: {e}")
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


def handle_user_choice_from_search_result(handler, response) -> Tuple[str, str]:
    """
    Handle user selection from search results.
    """
    if not response:
        log.debug("No result found!")
        sys.exit(0)
        
    if len(response) == 1:
        # single station found
        log.debug("Exactly one result found")

        try:
            user_input = input("Want to play this station? Y/N: ")
        except EOFError:
            print()
            sys.exit(0)

        if user_input in ["y", "Y"]:
            log.debug("Playing UUID from single response")
            # Update global info - handled via helper to ensure UI sees it
            set_global_station_info(response[0])

            return handle_station_uuid_play(handler, response[0]["stationuuid"])
        else:
            log.debug("Quitting")
            sys.exit(0)
    else:
        # multiple station
        log.debug("Asking for user input")

        try:
            log.info("Type 'r' to play a random station")
            user_input = input("Type the result ID to play: ")
        except EOFError:
            print()
            log.info("Exiting")
            log.debug("EOF reached, quitting")
            sys.exit(0)

        try:
            if user_input in ["r", "R", "random"]:
                # pick a random integer withing range
                user_input = randint(1, len(response) - 1)
                log.debug(f"Radom station id: {user_input}")
            # elif user_input in ["f", "F", "fuzzy"]:
            # fuzzy find all the stations, and return the selected station id
            # user_input = fuzzy_find(response)

            user_input = int(user_input) - 1  # because ID starts from 1
            if user_input in range(0, len(response)):
                target_response = response[user_input]
                log.debug(f"Selected: {target_response}")

                # saving global info
                set_global_station_info(target_response)

                return handle_station_uuid_play(handler, target_response["stationuuid"])
            else:
                log.error("Please enter an ID within the range")
                sys.exit(1)
        except ValueError:
             log.error("Please enter an valid ID number")
             sys.exit(1)
        except Exception as e:
            log.error(f"Error: {e}")
            sys.exit(1)


def handle_listen_keypress(
    alias,
    player,
    target_url,
    station_name,
    station_url,
    record_file_path,
    record_file,
    record_file_format,
    loglevel,
) -> None:
    """
    Listen for user input during playback to perform actions.
    """
    log.info("Press '?' to see available commands\n")
    while True:
        try:
            user_input = input("Enter a command to perform an action: ")
        except EOFError:
            print()
            log.debug("Ctrl+D (EOF) detected. Exiting gracefully.")
            kill_background_ffplays()
            sys.exit(0)

        if user_input in ["r", "R", "record"]:
            handle_record(
                target_url,
                station_name,
                record_file_path,
                record_file,
                record_file_format,
                loglevel,
            )
        elif user_input in ["rf", "RF", "recordfile"]:
            try:
                user_input = input("Enter output filename: ")
            except EOFError:
                print()
                log.debug("Ctrl+D (EOF) detected. Exiting gracefully.")
                kill_background_ffplays()
                sys.exit(0)

            # try to get extension from filename
            try:
                file_name_parts = user_input.split(".")
                if len(file_name_parts) > 1 and file_name_parts[-1] == "mp3":
                    log.debug("codec: force mp3")
                    # overwrite original codec with "mp3"
                    record_file_format = "mp3"
                    file_name = user_input.rsplit(".", 1)[0] # Handle filename with dots
                else:
                     # If user typed "file.mp3", we want file_name="file.mp3" probably?
                     # Original code logic: split('.') -> takes first part as name, second as ext.
                     # If ext is mp3, set force mp3.
                     # If user enters "my.song", it mistakes "song" for ext.
                     
                     if len(file_name_parts) > 1 and file_name_parts[-1] != "mp3":
                        log.warning("You can only specify mp3 as file extension.\n")
                        log.warning(
                            "Do not provide any extension to autodetect the codec.\n"
                        )
                     file_name = user_input 
            except Exception:
                file_name = user_input

            if user_input.strip() != "":
                handle_record(
                    target_url,
                    station_name,
                    record_file_path,
                    file_name,
                    record_file_format,
                    loglevel,
                )
        elif user_input in ["i", "I", "info"]:
            handle_show_station_info()

        elif user_input in ["f", "F", "fav"]:
            handle_add_to_favorite(alias, station_name, station_url)

        elif user_input in ["q", "Q", "quit"]:
            # kill_background_ffplays()
            player.stop()
            sys.exit(0)
        elif user_input in ["w", "W", "list"]:
            alias.generate_map()
            handle_favorite_table(alias)
        elif user_input in ["t", "T", "track"]:
            handle_fetch_song_title(target_url)
        elif user_input in ["p", "P"]:
            # toggle the player (start/stop)
            player.toggle()

        elif user_input in ["h", "H", "?", "help"]:
            log.info("p: Play/Pause current station")
            log.info("t/track: Current track info")
            log.info("i/info: Station information")
            log.info("r/record: Record a station")
            log.info("rf/recordfile: Specify a filename for the recording")
            log.info("f/fav: Add station to favorite list")
            log.info("h/help/?: Show this help message")
            log.info("q/quit: Quit radioactive")
