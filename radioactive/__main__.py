#!/usr/bin/env python
import os
import signal
import sys
from time import sleep

from rich.console import Console
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
    handle_current_play_panel,
    handle_direct_play,
    handle_favorite_table,
    handle_listen_keypress,
    handle_log_level,
    handle_record,
    handle_save_last_station,
    handle_search_stations,
    handle_station_selection_menu,
    handle_station_uuid_play,
    handle_update_screen,
    handle_user_choice_from_search_result,
    handle_welcome_screen,
)

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
    search_station_name = args.search_station_name
    direct_play = args.direct_play
    search_station_uuid = args.search_station_uuid

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
    record_file_format = args.record_file_format
    record_file_path = args.record_file_path

    target_url = ""

    VERSION = app.get_version()

    handler = Handler()
    alias = Alias()
    alias.generate_map()
    last_station = Last_station()

    # --------------- app logic starts here ------------------- #
    handle_welcome_screen()

    if args.version:
        log.info("RADIO-ACTIVE : version {}".format(VERSION))
        sys.exit(0)

    if show_help_table:
        show_help()
        sys.exit(0)
    handle_log_level(args)

    if flush_fav_list:
        sys.exit(alias.flush())

    if kill_ffplays:
        kill_background_ffplays()
        sys.exit(0)

    if show_favorite_list:
        handle_favorite_table(alias)
        sys.exit(0)

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
    # if neither of --search and --uuid provided
    if (
        search_station_name is None
        and search_station_uuid is None
        and direct_play is None
    ):
        curr_station_name, target_url = handle_station_selection_menu(
            handler, last_station, alias
        )

    # --------------------ONLY UUID PROVIDED --------------------- #

    if search_station_uuid is not None:
        curr_station_name, target_url = handle_station_uuid_play(
            handler, search_station_uuid
        )

    # ------------------- ONLY STATION PROVIDED ------------------ #

    elif (
        search_station_name is not None
        and search_station_uuid is None
        and direct_play is None
    ):
        response = [{}]
        response = handle_search_stations(handler, search_station_name, limit)
        if response is not None:
            curr_station_name, target_url = handle_user_choice_from_search_result(
                handler, response
            )
        else:
            sys.exit(0)
    # ------------------------- direct play ------------------------#
    if direct_play is not None:
        curr_station_name, target_url = handle_direct_play(alias, direct_play)

    # ---------------------- player ------------------------ #
    # check target URL for the last time
    if target_url.strip() == "":
        log.error("something is wrong with the url")
        sys.exit(1)

    if curr_station_name.strip() == "":
        curr_station_name = "N/A"

    global player
    player = Player(target_url, args.volume)

    handle_save_last_station(last_station, curr_station_name, target_url)

    if add_to_favorite:
        handle_add_to_favorite(alias, curr_station_name, target_url)

    handle_current_play_panel(curr_station_name)

    if record_stream:
        handle_record(
            target_url,
            curr_station_name,
            record_file_path,
            record_file,
            record_file_format,
        )

    handle_listen_keypress(
        alias=alias,
        target_url=target_url,
        station_name=curr_station_name,
        station_url=target_url,
        record_file_path=record_file_path,
        record_file=record_file,
        record_file_format=record_file_format,
    )

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
