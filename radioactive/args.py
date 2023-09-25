import argparse
import sys

from zenlog import log


class Parser:

    """Parse the command-line args and return result to the __main__"""

    def __init__(self):
        self.parser = None
        self.result = None

        self.parser = argparse.ArgumentParser(
            description="Play any radio around the globe right from the CLI ",
            prog="radio-active",
            add_help=False,
        )

        self.parser.add_argument(
            "--version", "-V", action="store_true", dest="version", default=False
        )
        self.parser.add_argument(
            "--help",
            "-H",
            action="store_true",
            default=False,
            dest="help",
            help="Show help message",
        )

        self.parser.add_argument(
            "--station",
            "-S",
            action="store",
            dest="station_name",
            help="Specify a station name",
        )

        self.parser.add_argument(
            "--uuid",
            "-U",
            action="store",
            dest="station_uuid",
            help="Specify a station UUID",
        )

        self.parser.add_argument(
            "--log-level",
            "-L",
            action="store",
            default="info",
            dest="log_level",
            help="Specify log level",
        )

        self.parser.add_argument(
            "--discover-by-country",
            "-D",
            action="store",
            dest="discover_country_code",
            help="Discover stations with country code",
        )

        self.parser.add_argument(
            "--discover-by-tag",
            action="store",
            dest="discover_tag",
            help="Discover stations with tag",
        )

        self.parser.add_argument(
            "--discover-by-state",
            action="store",
            dest="discover_state",
            help="Discover stations with state name",
        )

        self.parser.add_argument(
            "--discover-by-language",
            action="store",
            dest="discover_language",
            help="Discover stations with state name",
        )
        self.parser.add_argument(
            "--limit",
            action="store",
            dest="limit",
            default=100,
            help="Limit of entries in discover table",
        )

        self.parser.add_argument(
            "--add-station",
            "-A",
            action="store_true",
            default=False,
            dest="new_station",
            help="Add an entry to your favorite station",
        )

        self.parser.add_argument(
            "--add-to-favorite",
            "-F",
            action="store",
            dest="add_to_favorite",
            help="Save current station to your favorite list",
        )

        self.parser.add_argument(
            "--show-favorite-list",
            "-W",
            action="store_true",
            dest="show_favorite_list",
            default=False,
            help="Show your favorite list in table format",
        )

        self.parser.add_argument(
            "--flush",
            action="store_true",
            dest="flush",
            default=False,
            help="Flush your favorite list",
        )

        self.parser.add_argument(
            "--volume",
            action="store",
            dest="volume",
            default=80,
            type=int,
            choices=range(0, 101, 10),
            help="Volume to pass down to ffplay",
        )

        self.parser.add_argument(
            "--kill",
            action="store_true",
            dest="kill_ffplays",
            default=False,
            help="kill all the ffplay process initiated by radioactive",
        )

        self.parser.add_argument(
            "--record",
            "-R",
            action="store_true",
            dest="record_stream",
            default=False,
            help="record a station and save as audio file",
        )

        self.parser.add_argument(
            "--filename",
            action="store",
            dest="record_file",
            default="",
            help="specify the output filename of the recorded audio",
        )

    def parse(self):
        self.result = self.parser.parse_args()
        if self.result is None:
            log.error("Could not parse the arguments properly")
            sys.exit(1)
        return self.result
