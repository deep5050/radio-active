#!/usr/bin/env python
import os
import signal
import sys
from time import sleep

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
    handle_play_last_station,
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


def final_step(options, last_station, alias, handler):
    global player
    # check target URL for the last time
    if options["target_url"].strip() == "":
        log.error("something is wrong with the url")
        sys.exit(1)

    if options["curr_station_name"].strip() == "":
        options["curr_station_name"] = "N/A"

    player = Player(options["target_url"], options["volume"], options["loglevel"])

    handle_save_last_station(
        last_station, options["curr_station_name"], options["target_url"]
    )

    if options["add_to_favorite"]:
        handle_add_to_favorite(
            alias, options["curr_station_name"], options["target_url"]
        )

    handle_current_play_panel(options["curr_station_name"])

    if options["record_stream"]:
        handle_record(
            options["target_url"],
            options["curr_station_name"],
            options["record_file_path"],
            options["record_file"],
            options["record_file_format"],
            options["loglevel"],
        )

    handle_listen_keypress(
        alias,
        target_url=options["target_url"],
        station_name=options["curr_station_name"],
        station_url=options["target_url"],
        record_file_path=options["record_file_path"],
        record_file=options["record_file"],
        record_file_format=options["record_file_format"],
        loglevel=options["loglevel"],
    )


def main():
    log.level("info")
    parser = Parser()
    app = App()
    args = parser.parse()

    options = {}
    # ----------------- all the args ------------- #
    options["show_help_table"] = args.help
    options["search_station_name"] = args.search_station_name
    options["direct_play"] = args.direct_play
    options["play_last_station"] = args.play_last_station

    options["search_station_uuid"] = args.search_station_uuid

    options["discover_country_code"] = args.discover_country_code
    options["discover_state"] = args.discover_state
    options["discover_language"] = args.discover_language
    options["discover_tag"] = args.discover_tag

    limit = args.limit
    options["limit"] = int(limit) if limit else 100
    log.debug("limit is set to: {}".format(limit))

    options["add_station"] = args.new_station
    options["add_to_favorite"] = args.add_to_favorite
    options["show_favorite_list"] = args.show_favorite_list

    options["flush_fav_list"] = args.flush
    options["kill_ffplays"] = args.kill_ffplays

    options["record_stream"] = args.record_stream
    options["record_file"] = args.record_file
    options["record_file_format"] = args.record_file_format
    options["record_file_path"] = args.record_file_path

    options["target_url"] = ""
    options["volume"] = args.volume

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

    if options["show_help_table"]:
        show_help()
        sys.exit(0)

    options["loglevel"] = handle_log_level(args)

    if options["flush_fav_list"]:
        sys.exit(alias.flush())

    if options["kill_ffplays"]:
        kill_background_ffplays()
        sys.exit(0)

    if options["show_favorite_list"]:
        handle_favorite_table(alias)
        sys.exit(0)

    if options["add_station"]:
        handle_add_station(alias)

    handle_update_screen(app)

    # ----------- country ----------- #
    if options["discover_country_code"]:
        response = handler.discover_by_country(
            options["discover_country_code"], options["limit"]
        )
        if response is not None:
            (
                options["curr_station_name"],
                options["target_url"],
            ) = handle_user_choice_from_search_result(handler, response)
            final_step(options, last_station, alias, handler)
        else:
            sys.exit(0)

    # -------------- state ------------- #
    if options["discover_state"]:
        response = handler.discover_by_state(
            options["discover_state"], options["limit"]
        )
        if response is not None:
            (
                options["curr_station_name"],
                options["target_url"],
            ) = handle_user_choice_from_search_result(handler, response)
            final_step(options, last_station, alias, handler)
        else:
            sys.exit(0)

    # ----------- language ------------ #
    if options["discover_language"]:
        response = handler.discover_by_language(
            options["discover_language"], options["limit"]
        )
        if response is not None:
            (
                options["curr_station_name"],
                options["target_url"],
            ) = handle_user_choice_from_search_result(handler, response)
            final_step(options, last_station, alias, handler)
        else:
            sys.exit(0)

    # -------------- tag ------------- #
    if options["discover_tag"]:
        response = handler.discover_by_tag(options["discover_tag"], options["limit"])
        if response is not None:
            (
                options["curr_station_name"],
                options["target_url"],
            ) = handle_user_choice_from_search_result(handler, response)
            final_step(options, last_station, alias, handler)
        else:
            sys.exit(0)

    # -------------------- NOTHING PROVIDED --------------------- #
    if (
        options["search_station_name"] is None
        and options["search_station_uuid"] is None
        and options["direct_play"] is None
        and not options["play_last_station"]
    ):
        (
            options["curr_station_name"],
            options["target_url"],
        ) = handle_station_selection_menu(handler, last_station, alias)
        final_step(options, last_station, alias, handler)

    # --------------------ONLY UUID PROVIDED --------------------- #

    if options["search_station_uuid"] is not None:
        options["curr_station_name"], options["target_url"] = handle_station_uuid_play(
            handler, options["search_station_uuid"]
        )
        final_step(options, last_station, alias, handler)

    # ------------------- ONLY STATION PROVIDED ------------------ #

    elif (
        options["search_station_name"] is not None
        and options["search_station_uuid"] is None
        and options["direct_play"] is None
    ):
        response = [{}]
        response = handle_search_stations(
            handler, options["search_station_name"], options["limit"]
        )
        if response is not None:
            (
                options["curr_station_name"],
                options["target_url"],
            ) = handle_user_choice_from_search_result(handler, response)
            # options["codec"] = response["codec"]
            # print(response)
            final_step(options, last_station, alias, handler)
        else:
            sys.exit(0)
    # ------------------------- direct play ------------------------#
    if options["direct_play"] is not None:
        options["curr_station_name"], options["target_url"] = handle_direct_play(
            alias, options["direct_play"]
        )
        final_step(options, last_station, alias, handler)

    if options["play_last_station"]:
        options["curr_station_name"], options["target_url"] = handle_play_last_station(
            last_station
        )
        final_step(options, last_station, alias, handler)

    # final_step()

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
