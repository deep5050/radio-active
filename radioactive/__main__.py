#!/usr/bin/env python
import signal
import sys

import sentry_sdk
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from zenlog import log

from radioactive.alias import Alias
from radioactive.app import App
from radioactive.args import Parser
from radioactive.handler import Handler
from radioactive.help import show_help
from radioactive.last_station import Last_station
from radioactive.player import Player

# globally needed as signal handler needs it
# to terminate main() properly
player = None


def main():
    sentry_sdk.init(
        "https://e3c430f3b03f49b6bd9e9d61e7b3dc37@o615507.ingest.sentry.io/5749950",
        traces_sample_rate=1.0,
        debug=False,
    )

    log.level("info")

    parser = Parser()
    app = App()
    args = parser.parse()

    ############ all the args ############
    show_help_table = args.help
    station_name = args.station_name
    station_uuid = args.station_uuid
    log_level = args.log_level
    discover = args.discover
    add_station = args.new_station
    add_to_favourite = args.add_to_favourite
    show_favourite_list = args.show_favourite_list
    flush_fav_list = args.flush
    ########################################

    VERSION = app.get_version()
    if args.version:
        log.info("RADIO-ACTIVE : version {}".format(VERSION))
        sys.exit(0)

    if show_help_table:
        show_help()
        sys.exit(0)

    if log_level in ["info", "error", "warning", "debug"]:
        log.level(log_level)
    else:
        log.warning("Correct log levels are: error,warning,info(default),debug")

    handler = Handler()
    alias = Alias()
    alias.generate_map()
    last_station = Last_station()

    mode_of_search = ""
    direct_play = False
    direct_play_url = ""
    skip_saving_current_station = False
    is_alias = False

    ################################# RICH ##################
    console = Console()

    welcome = Panel(
        """
        :radio: Play any radios around the globe right from this Terminal [yellow][blink]:zap:[/blink][/yellow]!
        :smile: Author: Dipankar Pal
        :question: Type '--help' for more details on avaliable commands.
        :bug: Visit https://github.com/deep5050/radio-active to submit issues
        :star: Show some love by starring the project on GitHub [red][blink]:heart:[/blink][/red]
        :x: Press Ctrl+C to quit
        """,
        title="[rgb(250,0,0)]RADIO[rgb(0,255,0)]ACTIVE",
        width=85,
    )
    print(welcome)

    if app.is_update_available():
        update_msg = (
            "\t[blink]An update available, run [green][italic]pip install radio-active=="
            + app.get_remote_version()
            + "[/italic][/green][/blink]"
        )
        update_panel = Panel(
            update_msg,
            width=85,
        )
        print(update_panel)
    else:
        log.debug("Update not available")

    if flush_fav_list:
        alias.flush()

    if show_favourite_list:
        log.info("Your favourite station list is below")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Station", justify="left")
        table.add_column("URL / UUID", justify="center")
        if len(alias.alias_map) > 0:
            for entry in alias.alias_map:
                table.add_row(entry["name"], entry["uuid_or_url"])
            console.print(table)
        else:
            log.info("You have no favourite station list")
        sys.exit(0)

    if add_station:
        left = input("Enter station name:")
        right = input("Enter station stream-url or radio-browser uuid:")
        if left.strip() == "" or right.strip() == "":
            log.error("Empty inputs not allowed")
            sys.exit(1)
        alias.add_entry(left, right)
        log.info("New entry: {}={} added\n".format(left, right))
        sys.exit(0)

    # -------------------- NOTHING PROVIDED --------------------- #
    # if neither of --station and --uuid provided , look in last_station file

    if station_name is None and station_uuid is None:
        # try to fetch the last played station's information
        log.warn("No station information provided, trying to play the last station")

        last_station_info = last_station.get_info()

        try:
            if last_station_info["alias"]:
                is_alias = True
        except:
            pass

        if is_alias:
            alias.found = True  # save on last_play as an alias too!
            # last stattion was an alias, don't save it again
            skip_saving_current_station = True
            station_uuid_or_url = last_station_info["uuid_or_url"]
            if station_uuid_or_url.find("://") != -1:
                # Its a URL
                log.debug(
                    "Last station was an alias and contains a URL, Direct play set to True"
                )
                direct_play = True
                direct_play_url = station_uuid_or_url
                log.info("Current station: {}".format(last_station_info["name"]))
            else:
                # an UUID
                station_uuid = last_station_info["uuid_or_url"]
        else:
            # was not an alias
            station_uuid = last_station_info["stationuuid"]

        # getting last station details, getting the UUID
        # station_uuid_or_url = last_station.get_info()
        # station_name =
        # if station_uuid_or_url.find("://") != -1:
        #     # Its a URL
        #     log.debug("Last station was an alias and contains a URL, Direct play set to True")
        #     direct_play = True
        #     direct_play_url = station_uuid_or_url
        # else:
        #     log.debug("Last station was an alias and contains UUID")
        #     station_uuid = station_uuid_or_url

    # ------------------------------------------------------------ #

    # --------------------ONLY UUID PROVIDED --------------------- #
    # if --uuid provided call directly
    result = None
    if station_uuid is not None:
        mode_of_search = "uuid"

    # ------------------------------------------------------------ #

    # ------------------- ONLY STATION PROVIDED ------------------ #

    elif station_name is not None and station_uuid is None:
        # got station name only, looking in alias (if any)

        result = alias.search(station_name)
        if result is not None and alias.found:
            try:
                station_uuid_or_url = result["uuid_or_url"]
                # check if it is a url or a uuid
                if station_uuid_or_url.find("://") != -1:
                    # its a URL
                    log.debug("Entry contains a URL")
                    log.debug("Direct play set to True ")
                    log.info("current station: {}".format(result["name"]))
                    direct_play = True
                    # assigning url and name directly
                    direct_play_url = result["uuid_or_url"]
                    # handler.target_station['name'] = result["name"]
                    # handler.target_station["url"] = result["uuid_or_url"]
                else:
                    log.debug("Entry contains a UUID")
                    # mode_of_search = "uuid"
                    station_uuid = result["uuid_or_url"]  # its a UUID

            except:
                log.warning("Station found in favourite list but seems to be invalid")
                log.warning("Looking on the web instead")
                # log.warning("URL or UUID missing for the entry in favourite list, looking in the web instead")
                # sys.exit(1)
                alias.found = False

        if alias.found:
            mode_of_search = "uuid"
            if not direct_play:
                log.debug("Looking on the web for given UUID")

        else:
            log.debug("Alias not found, using normal API search")
            mode_of_search = "name"
    # ------------------------------------------------------------ #

    # log.debug("Mode of search: {}".format(mode_of_search))

    if not direct_play:
        # avoid extra API calls since target url is given
        if mode_of_search == "uuid":
            handler.play_by_station_uuid(station_uuid)
        else:
            handler.play_by_station_name(station_name)

    global player

    target_url = direct_play_url if direct_play else handler.target_station["url"]
    player = Player(target_url)

    # writing the station name to a file, next time if user
    # don't specify anything, it will try to start the last station
    last_played_station = {}
    if not alias.found:
        # station was not in the alias file
        last_played_station = handler.target_station
    else:
        last_played_station["name"] = station_name
        last_played_station["uuid_or_url"] = station_uuid_or_url
        last_played_station["alias"] = True

    if not skip_saving_current_station:
        last_station.save_info(last_played_station)

    # TODO: handle error when favouriting last played (aliased) station (BUG) (LOW PRIORITY)
    if add_to_favourite:
        alias.add_entry(add_to_favourite, handler.target_station["url"])

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
