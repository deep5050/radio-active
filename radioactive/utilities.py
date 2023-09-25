"""Handler functions for __main__.py"""

import datetime
import sys

from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from zenlog import log

from radioactive.app import App
from radioactive.recorder import record_audio_from_url


def handle_log_level(args):
    log_level = args.log_level
    if log_level in ["info", "error", "warning", "debug"]:
        log.level(log_level)
    else:
        log.warning("Correct log levels are: error,warning,info(default),debug")


def handle_record(target_url, curr_station_name, record_file):
    log.info("Press 'q' to stop recording")

    now = datetime.datetime.now()
    formatted_date_time = now.strftime("%y-%m-%d-%H:%M:%S")

    if not record_file:
        record_file = "{}-{}".format(
            curr_station_name.strip(), formatted_date_time
        ).replace(" ", "-")

    log.info(f"Recording will be saved as: {record_file}.mp3")

    record_audio_from_url(target_url, f"{record_file}.mp3")


def handle_welcome_screen():
    welcome = Panel(
        """
        :radio: Play any radios around the globe right from this Terminal [yellow]:zap:[/yellow]!
        :smile: Author: Dipankar Pal
        :question: Type '--help' for more details on available commands
        :bug: Visit: https://github.com/deep5050/radio-active to submit issues
        :star: Show some love by starring the project on GitHub [red]:heart:[/red]
        :dollar: You can donate me at https://deep5050.github.io/payme/
        :x: Press Ctrl+C to quit
        """,
        title="[b]RADIOACTIVE[/b]",
        width=85,
    )
    print(welcome)


def handle_update_screen(app):
    if app.is_update_available():
        update_msg = (
            "\t[blink]An update available, run [green][italic]pip install radio-active=="
            + app.get_remote_version()
            + "[/italic][/green][/blink]\nSee the changes: https://github.com/deep5050/radio-active/blob/main/CHANGELOG.md"
        )
        update_panel = Panel(
            update_msg,
            width=85,
        )
        print(update_panel)
    else:
        log.debug("Update not available")


def handle_favorite_table(alias):
    log.info("Your favorite station list is below")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Station", justify="left")
    table.add_column("URL / UUID", justify="center")
    if len(alias.alias_map) > 0:
        for entry in alias.alias_map:
            table.add_row(entry["name"], entry["uuid_or_url"])
        print(table)
        log.info(f"Your favorite stations are saved in {alias.alias_path}")
    else:
        log.info("You have no favorite station list")
    sys.exit(0)


def handle_add_station(alias):
    left = input("Enter station name:")
    right = input("Enter station stream-url or radio-browser uuid:")
    if left.strip() == "" or right.strip() == "":
        log.error("Empty inputs not allowed")
        sys.exit(1)
    alias.add_entry(left, right)
    log.info("New entry: {}={} added\n".format(left, right))
    sys.exit(0)


def handle_add_to_favorite(add_to_favorite, alias, handler):
    try:
        alias.add_entry(add_to_favorite, handler.target_station["url"])
    except Exception as e:
        log.debug("Error: {}".format(e))
        log.error("Could not add to favorite. Already in list?")


def handle_uuid_play():
    pass
