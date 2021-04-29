import argparse


class Parser:
    def __init__(self):
        self.parser = None
        self.result = None

        self.parser = argparse.ArgumentParser(
            description="Play any radio around the globe right from the CLI ",
            prog="radio-active",
        )

        self.parser.add_argument(
            "--version", "-V", action="store_true", dest="version", default=False
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

    def parse(self):
        self.result = self.parser.parse_args()

        if self.result is None:
            log.error("Could not parse the arguments properly")
            sys.exit(1)
        return self.result
