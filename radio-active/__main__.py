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

last_station_path = os.path.join(os.path.expanduser("~"), ".last_station.json")


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

    if station_name is None and station_uuid is None:
        # try to fetch the last played station's information
        log.warn(
            "No station information provided, trying to get the last station information"
        )
        try:
            with open(last_station_path, "r") as f:
                last_station = json.load(f)
                f.close()
                station_uuid = last_station["stationuuid"]
        except Exception as e:
            log.critical("Need a station name  or UUID to play the radio, see help")
            sys.exit(0)

    # log.debug("Station name: " + station_name)

    handler = Handler()
    target_station = None
    # uuid gets first preference

    if station_uuid is not None and station_name is not None:
        log.info(
            "Both station name and UUID are provided, selecting UUID to find the station"
        )

    if station_uuid is not None:
        log.debug("Started with UUID mode")
        handler.play_by_station_uuid(station_uuid)

    if station_uuid is None and station_name is not None:
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
