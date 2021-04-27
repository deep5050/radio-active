import sys
import signal
import argparse

from zenlog import log
from handler import Handler
from player import Player

player = None


def signal_handler(sig, frame):
    global player
    log.debug("You pressed Ctrl+C!")
    log.debug("Stopping the radio")
    if player.is_playing:
        player.stop()
    log.debug("Exiting now")
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
        log.critical("Need a station name  or UUID to play the radio, see help")
        sys.exit(0)

    # log.debug("Station name: " + station_name)

    handler = Handler()
    target_station = None
    # uuid gets first preference
    if station_uuid is not None:
        handler.play_by_station_uuid(station_uuid)
    if station_uuid is None and station_name is not None:
        handler.play_by_station_name(station_name)
    global player
    player = Player(handler.target_station["url"])

    signal.pause()


main()
