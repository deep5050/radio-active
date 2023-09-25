#!/usr/bin/env python
import os
import signal
import sys
from time import sleep

from pick import pick
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from zenlog import log

from radioactive.alias import Alias
from radioactive.app import App
from radioactive.args import Parser
from radioactive.handler import Handler
from radioactive.help import show_help
from radioactive.last_station import Last_station
from radioactive.player import Player, kill_background_ffplays
from radioactive.utilities import (
    handle_add_station,
    handle_add_to_favorite,
    handle_favorite_table,
    handle_log_level,
    handle_record,
    handle_update_screen,
    handle_welcome_screen,
)

RED_COLOR = "\033[91m"
END_COLOR = "\033[0m"

# globally needed as signal handler needs it
# to terminate main() properly
player = None


def main():
    log.level("info")
    parser = Parser()
    app = App()
    args = parser.parse()

    # ----------------- all the args ------------- #
    show_help_table = args.help
    station_name = args.station_name
    station_uuid = args.station_uuid

    discover_country_code = args.discover_country_code
    discover_state = args.discover_state
    discover_language = args.discover_language
    discover_tag = args.discover_tag

    limit = args.limit
    limit = int(limit) if limit else 100
    log.debug("limit is set to: {}".format(limit))

    add_station = args.new_station
    add_to_favorite = args.add_to_favorite
    show_favorite_list = args.show_favorite_list
    flush_fav_list = args.flush
    kill_ffplays = args.kill_ffplays
    record_stream = args.record_stream
    record_file = args.record_file

    VERSION = app.get_version()

    if args.version:
        log.info("RADIO-ACTIVE : version {}".format(VERSION))
        sys.exit(0)

    if show_help_table:
        show_help()
        sys.exit(0)

    mode_of_search = ""
    direct_play = False
    direct_play_url = ""
    skip_saving_current_station = False
    console = Console()

    handler = Handler()
    alias = Alias()
    alias.generate_map()
    last_station = Last_station()

    # --------------- app logic starts here ------------------- #
    handle_welcome_screen()
    handle_log_level(args)

    if flush_fav_list:
        sys.exit(alias.flush())

    if kill_ffplays:
        kill_background_ffplays()
        sys.exit(0)

    if show_favorite_list:
        handle_favorite_table(alias)

    if add_station:
        handle_add_station(alias)

    handle_update_screen(app)

    if discover_country_code:
        handler.discover_by_country(discover_country_code, limit)

    if discover_state:
        handler.discover_by_state(discover_state, limit)

    if discover_language:
        handler.discover_by_language(discover_language, limit)

    if discover_tag:
        handler.discover_by_tag(discover_tag, limit)

    # -------------------- NOTHING PROVIDED --------------------- #
    # if neither of --station and --uuid provided , look in last_station file

    if station_name is None and station_uuid is None:
        # Add a selection list here. first entry must be the last played station
        # try to fetch the last played station's information

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
            # setting message color to red. technically it is not an error though.
            # doing it just to catch user attention :)
            log.info(
                f"{RED_COLOR}No stations to play. please search for a station first!{END_COLOR}"
            )
            sys.exit(0)

        _, index = pick(options, title, indicator="-->")

        # check if there is direct URL or just UUID
        station_option_url = station_selection_urls[index]
        station_name = station_selection_names[index].replace(
            "(last played station)", ""
        )

        if station_option_url.find("://") != -1:
            # set direct play to TRUE
            direct_play = True
            direct_play_url = station_option_url
        else:
            # UUID
            station_uuid = station_option_url

    # --------------------ONLY UUID PROVIDED --------------------- #
    # if --uuid provided call directly
    result = None
    if station_uuid is not None:
        mode_of_search = "uuid"
        log.debug("increased click count for: {}".format(station_uuid))
        handler.vote_for_uuid(station_uuid)

    # ------------------- ONLY STATION PROVIDED ------------------ #

    elif station_name is not None and station_uuid is None:
        # got station name only, looking in alias (if any)

        result = alias.search(station_name)
        if result is not None and alias.found:
            try:
                station_uuid_or_url = result["uuid_or_url"]
                # check if it is a url or a uuid
                if station_uuid_or_url.find("://") != -1:
                    # its a URL
                    log.debug("Entry contains a URL")
                    log.debug("Direct play set to True ")
                    log.info("Current station: {}".format(result["name"]))
                    direct_play = True
                    # assigning url and name directly
                    direct_play_url = result["uuid_or_url"]
                else:
                    log.debug("Entry contains a UUID")
                    # mode_of_search = "uuid"
                    station_uuid = result["uuid_or_url"]  # its a UUID
                    handler.vote_for_uuid(station_uuid)

            except Exception as e:
                log.debug("Error: {}".format(e))
                log.warning("Station found in favorite list but seems to be invalid")
                log.warning("Looking on the web instead")
                alias.found = False

        if alias.found:
            mode_of_search = "uuid"
            if not direct_play:
                log.debug("Looking on the web for given UUID")

        else:
            log.debug("Alias not found, using normal API search")
            mode_of_search = "name"

    if not direct_play:
        # avoid extra API calls since target url is given
        if mode_of_search == "uuid":
            _station_name = handler.play_by_station_uuid(station_uuid)
            station_name = _station_name
        else:
            if not alias.found:
                # when alias was found, we have set the station name to print it correctly,
                # not to do an API call
                handler.play_by_station_name(station_name, limit)

    global player

    target_url = direct_play_url if direct_play else handler.target_station["url"]
    player = Player(target_url, args.volume)

    # writing the station name to a file, next time if user
    # don't specify anything, it will try to start the last station
    last_played_station = {}
    if not alias.found:
        # station was not in the alias file
        last_played_station = handler.target_station
    else:
        last_played_station["name"] = station_name
        last_played_station["uuid_or_url"] = station_uuid_or_url
        last_played_station["alias"] = True

    if not skip_saving_current_station:
        log.debug(f"Saving the current station: {last_played_station}")
        if last_played_station:
            last_station.save_info(last_played_station)

    # TODO: handle error when favouring last played (aliased) station (BUG) (LOW PRIORITY)
    if add_to_favorite:
        handle_add_to_favorite(add_to_favorite, alias, handler)

    curr_station_name = station_name

    try:
        # TODO fix this. when aliasing a station with an existing name
        # curr_station_name is being None
        panel_station_name = Text(curr_station_name, justify="center")

        station_panel = Panel(
            panel_station_name, title="[blink]:radio:[/blink]", width=85
        )

        console.print(station_panel)

        if record_stream:
            handle_record(target_url, curr_station_name, record_file)

    except Exception as e:
        log.debug("Error: {}".format(e))
        # TODO handle exception
        pass

    if os.name == "nt":
        while True:
            sleep(5)
    else:
        try:
            signal.pause()
        except Exception as e:
            log.debug("Error: {}".format(e))
            pass


def signal_handler(sig, frame):
    global player
    log.debug("You pressed Ctrl+C!")
    log.debug("Stopping the radio")
    if player and player.is_playing:
        player.stop()
    log.info("Exiting now")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    main()
