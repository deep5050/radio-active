#!/usr/bin/ python3

import sys
import os
import signal
import argparse
import json
from zenlog import log
from handler import Handler
from player import Player

player = None

last_station_path = os.path.join(
    os.path.expanduser("~"), ".radio-active-last-station.json"
)
alias_path = os.path.join(os.path.expanduser("~"), "radio-active-alias.txt")


def signal_handler(sig, frame):
    global player
    log.debug("You pressed Ctrl+C!")
    log.debug("Stopping the radio")
    if player.is_playing:
        player.stop()
    log.info("Exiting now")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def main():
    handler = Handler()
    target_station = None
    mode_of_search = ""
    alias_map = []

    parser = argparse.ArgumentParser(
        description="Play any radio around the globe right from the CLI ",
        prog="radio-active",
    )

    parser.add_argument("--version", action="version", version="%(prog)s 1.0")

    parser.add_argument(
        "--station",
        action="store",
        dest="station_name",
        help="Specify a station name",
    )
    parser.add_argument(
        "--uuid",
        action="store",
        dest="station_uuid",
        help="Specify a station UUID",
    )

    parser.add_argument(
        "--log-level",
        action="store",
        default="info",
        dest="log_level",
        help="Specify log level",
    )

    args = parser.parse_args()

    station_name = args.station_name
    station_uuid = args.station_uuid
    log_level = args.log_level

    if log_level in ["info", "error", "debug"]:
        log.level(log_level)
    else:
        log.level("info")
        log.warning("Correct log levels are: error,warning,info(default),debug")

    # create alias map
    try:
        with open(alias_path, "r") as f:
            log.debug("Alias file exists")
            alias_data = f.read()
            f.close()
            alias_list = alias_data.splitlines()
            for alias in alias_list:
                temp = alias.split("=")
                left = temp[0]
                right = temp[1]
                alias_map.append({"name": left, "uuid": right})
                log.debug("[ {} = {} ]".format(left, right))

            # log.debug(json.dumps(alias_map, indent=3))

    except Exception as e:
        log.warning("could not get / parse alias data")

    # if neither of --station and --uuid provided , look in last_station file
    if station_name is None and station_uuid is None:
        # try to fetch the last played station's information
        log.warn(
            "No station information provided, trying to get the last station information"
        )
        # getting last station details
        try:
            with open(last_station_path, "r") as f:
                last_station = json.load(f)
                f.close()
                station_uuid = last_station["stationuuid"]
                log.info("Playing last station: {}".format(last_station["name"]))
        except Exception as e:
            log.critical("Need a station name  or UUID to play the radio, see help")
            sys.exit(0)
        #################################

    alias_found = False

    # if --uuid provided call directly
    if station_uuid is not None:
        mode_of_search = "uuid"

    elif station_name is not None and station_uuid is None:
        # got station name only, looking in alias first
        # look for alias file (if any)
        if len(alias_map) > 0:
            log.debug("looking under alias file")
            for alias in alias_map:
                if alias["name"] == station_name:
                    station_uuid = alias["uuid"]
                    log.debug(
                        "Alias found: {} = {}".format(alias["name"], alias["uuid"])
                    )
                    alias_found = True
                    break

        if alias_found == True:
            # log.debug("Started with UUID mode")
            mode_of_search = "uuid"
        else:
            log.debug("Alias not found, using normal API search")
            mode_of_search = "name"

    log.debug("Mode of search: {}".format(mode_of_search))

    if mode_of_search == "uuid":
        handler.play_by_station_uuid(station_uuid)

    else:
        handler.play_by_station_name(station_name)

    global player
    player = Player(handler.target_station["url"])

    # writing the station name to a file, next time if user
    # don't specify anything will try to start the last station

    log.debug("Dumping station information")
    with open(last_station_path, "w") as f:
        json.dump(handler.target_station, f)
        f.close()

    signal.pause()


if __name__ == "__main__":
    main()
