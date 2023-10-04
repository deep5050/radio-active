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
            "--version", action="store_true", dest="version", default=False
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
            "--search",
            "-S",
            action="store",
            dest="search_station_name",
            help="Specify a station name",
        )
        self.parser.add_argument(
            "--play",
            "-P",
            action="store",
            dest="direct_play",
            help="Specify a station from fav list or direct url",
        )

        self.parser.add_argument(
            "--last",
            action="store_true",
            default=False,
            dest="play_last_station",
            help="Play last played station.",
        )

        self.parser.add_argument(
            "--uuid",
            "-U",
            action="store",
            dest="search_station_uuid",
            help="Specify a station UUID",
        )

        self.parser.add_argument(
            "--loglevel",
            action="store",
            default="info",
            dest="log_level",
            help="Specify log level",
        )

        self.parser.add_argument(
            "--country",
            "-C",
            action="store",
            dest="discover_country_code",
            help="Discover stations with country code",
        )

        self.parser.add_argument(
            "--tag",
            action="store",
            dest="discover_tag",
            help="Discover stations with tag",
        )

        self.parser.add_argument(
            "--state",
            action="store",
            dest="discover_state",
            help="Discover stations with state name",
        )

        self.parser.add_argument(
            "--language",
            action="store",
            dest="discover_language",
            help="Discover stations with state name",
        )
        self.parser.add_argument(
            "--limit",
            "-L",
            action="store",
            dest="limit",
            default=100,
            help="Limit of entries in discover table",
        )

        self.parser.add_argument(
            "--add",
            "-A",
            action="store_true",
            default=False,
            dest="new_station",
            help="Add an entry to your favorite station",
        )

        self.parser.add_argument(
            "--favorite",
            "-F",
            action="store",
            dest="add_to_favorite",
            help="Save current station to your favorite list",
        )

        self.parser.add_argument(
            "--list",
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
            "-V",
            action="store",
            dest="volume",
            default=80,
            type=int,
            choices=range(0, 101, 10),
            help="Volume to pass down to ffplay",
        )

        self.parser.add_argument(
            "--kill",
            "-K",
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
            "--filepath",
            action="store",
            dest="record_file_path",
            default="",
            help="specify the audio format for recording",
        )

        self.parser.add_argument(
            "--filename",
            "-N",
            action="store",
            dest="record_file",
            default="",
            help="specify the output filename of the recorded audio",
        )

        self.parser.add_argument(
            "--filetype",
            "-T",
            action="store",
            dest="record_file_format",
            default="mp3",
            help="specify the audio format for recording. auto/mp3",
        )

    def parse(self):
        self.result = self.parser.parse_args()
        if self.result is None:
            log.error("Could not parse the arguments properly")
            sys.exit(1)
        return self.result
