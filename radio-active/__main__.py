#!/usr/bin/ python3

import sys
import os
import signal
import argparse
import json
from zenlog import log

from __init__ import get_version
from args import Parser
from alias import Alias
from handler import Handler
from player import Player
from last_station import Last_station


# globally needed as signal handler needs it
# to terminate main() properly
player = None


def main():
    parser = Parser()
    args = parser.parse()

    handler = Handler()

    alias = Alias()
    alias.generate_map()

    last_station = Last_station()

    mode_of_search = ""
    VERSION = get_version()

    if args.version:
        log.info("RADIO-ACTIVE : version {}".format(VERSION))
        sys.exit(0)

    station_name = args.station_name
    station_uuid = args.station_uuid
    log_level = args.log_level

    if log_level in ["info", "error", "debug"]:
        log.level(log_level)
    else:
        log.level("info")
        log.warning("Correct log levels are: error,warning,info(default),debug")

    # -------------------- NOTHING PROVIDED --------------------- #
    # if neither of --station and --uuid provided , look in last_station file

    if station_name is None and station_uuid is None:
        # try to fetch the last played station's information
        log.warn("No station information provided, trying to get the last station")
        # getting last station details, getting the UUID
        station_uuid = last_station.get_info()

    # ------------------------------------------------------------ #

    # --------------------ONLY UUID PROVIDED --------------------- #
    # if --uuid provided call directly

    if station_uuid is not None:
        mode_of_search = "uuid"

    # ------------------------------------------------------------ #

    # ------------------- ONLY STATION PROVIDED ------------------ #

    elif station_name is not None and station_uuid is None:
        # got station name only, looking in alias (if any)

        result = alias.search(station_name)
        if result is not None and alias.found:
            station_uuid = result["stationuuid"]

        if alias.found == True:
            mode_of_search = "uuid"
        else:
            log.debug("Alias not found, using normal API search")
            mode_of_search = "name"
    # ------------------------------------------------------------ #

    log.debug("Mode of search: {}".format(mode_of_search))

    if mode_of_search == "uuid":
        handler.play_by_station_uuid(station_uuid)

    else:
        handler.play_by_station_name(station_name)

    global player
    player = Player(handler.target_station["url"])

    # writing the station name to a file, next time if user
    # don't specify anything, it will try to start the last station
    last_station.save_info(handler.target_station)

    signal.pause()


def signal_handler(sig, frame):
    global player
    log.debug("You pressed Ctrl+C!")
    log.debug("Stopping the radio")
    if player.is_playing:
        player.stop()
    log.info("Exiting now")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


if __name__ == "__main__":
    main()
