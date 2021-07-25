#!/usr/bin/env python
import signal
import sys
import os
from time import sleep

from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
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
    log.level("info")
    parser = Parser()
    app = App()
    args = parser.parse()

    ############ all the args ############
    show_help_table = args.help
    station_name = args.station_name
    station_uuid = args.station_uuid
    log_level = args.log_level

    discover_country_code = args.discover_country_code
    discover_state = args.discover_state
    discover_language = args.discover_language
    discover_tag = args.discover_tag

    limit = args.limit
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
        title="[b][rgb(250,0,0)]RADIO[rgb(0,255,0)]ACTIVE[/b]",
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


# ------------------ discover ------------------ #
    _limit = int(limit) if limit else 100

    if discover_country_code:
        # search for stations in your country 
        handler.discover_by_country(discover_country_code,_limit)
    
    if discover_state:
        handler.discover_by_state(discover_state,_limit)

    if discover_language:
        handler.discover_by_language(discover_language,_limit)
    
    if discover_tag:
        handler.discover_by_tag(discover_tag,_limit)


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
            # last station was an alias, don't save it again
            skip_saving_current_station = True
            station_uuid_or_url = last_station_info["uuid_or_url"]
            station_name = last_station_info['name'] # here we are setting the name but will not be used for API call
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

    # --------------------ONLY UUID PROVIDED --------------------- #
    # if --uuid provided call directly
    result = None
    if station_uuid is not None:
        mode_of_search = "uuid"

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
                else:
                    log.debug("Entry contains a UUID")
                    # mode_of_search = "uuid"
                    station_uuid = result["uuid_or_url"]  # its a UUID

            except:
                log.warning("Station found in favourite list but seems to be invalid")
                log.warning("Looking on the web instead")
                alias.found = False

        if alias.found:
            mode_of_search = "uuid"
            if not direct_play:
                log.debug("Looking on the web for given UUID")

        else:
            log.debug("Alias not found, using normal API search")
            mode_of_search = "name"

    if not direct_play:
        # avoid extra API calls since target url is given
        if mode_of_search == "uuid":
            handler.play_by_station_uuid(station_uuid)
        else:
            if not alias.found:
                # when alias was found, we have set the station name to print it correctly,
                # not to do an API call
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

    # TODO: handle error when favouring last played (aliased) station (BUG) (LOW PRIORITY)
    if add_to_favourite:
        alias.add_entry(add_to_favourite, handler.target_station["url"])


    curr_station_name =   station_name if alias.found else handler.target_station['name']
    panel_station_name = Text(curr_station_name,justify="center")

    station_panel = Panel(panel_station_name,title="[blink]:radio:[/blink]",width=85)
    console.print(station_panel)

    if os.name == "nt":
        while True:
            sleep(5)
    else:
        try:
            signal.pause()
        except:
            pass


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
