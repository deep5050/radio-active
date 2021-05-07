import argparse
import sys
from zenlog import log


class Parser:

    """Parse the command-line args and retrun result to the __main__"""

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
            "--discover",
            "-D",
            action="store",
            dest="discover",
            help="Discover stations in your country",
        )

        self.parser.add_argument(
            "--add-station",
            "-A",
            action="store_true",
            default=False,
            dest="new_station",
            help="Add an entry to your favourite station",
        )

        self.parser.add_argument(
            "--add-to-favourite",
            "-F",
            action="store",
            dest="add_to_favourite",
            help="Save current station to your favourite list",
        )

        self.parser.add_argument(
            "--show-favourite-list",
            "-W",
            action="store_true",
            dest="show_favourite_list",
            default=False,
            help="Show your favourite list in table format",
        )

        self.parser.add_argument(
            "--random",
            "-R",
            action="store_true",
            dest="random",
            default=False,
            help="Play a random station from your favourite list",
        )

        self.parser.add_argument(
            "--flush",
            action="store_true",
            dest="flush",
            default=False,
            help="Flush your favourite list",
        )

    def parse(self):
        self.result = self.parser.parse_args()

        if self.result is None:
            log.error("Could not parse the arguments properly")
            sys.exit(1)
        return self.result
