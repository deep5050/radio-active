"""Handler functions for __main__.py"""

import datetime
import json
import os
import subprocess
import sys
from random import randint

import requests
from pick import pick
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from zenlog import log

from radioactive.ffplay import kill_background_ffplays
from radioactive.last_station import Last_station
from radioactive.recorder import record_audio_auto_codec, record_audio_from_url

RED_COLOR = "\033[91m"
END_COLOR = "\033[0m"

global_current_station_info = {}
# Global variable to store last search results for cycle functionality
global_last_search_results = []


def handle_fetch_song_title(url):
    """Fetch currently playing track information"""
    log.info("Fetching the current track info")
    log.debug("Attempting to retrieve track info from: {}".format(url))
    # Run ffprobe command and capture the metadata
    cmd = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_entries",
        "format=icy",
        url,
    ]
    track_name = ""

    try:
        output = subprocess.check_output(cmd).decode("utf-8")
        data = json.loads(output)
        log.debug(f"station info: {data}")

        # Extract the station name (icy-name) if available
        track_name = data.get("format", {}).get("tags", {}).get("StreamTitle", "")
    except:
        log.error("Error while fetching the track name")

    if track_name != "":
        log.info(f"🎶: {track_name}")
    else:
        log.error("No track information available")


def handle_record(
    target_url,
    curr_station_name,
    record_file_path,
    record_file,
    record_file_format,  # auto/mp3
    loglevel,
):
    log.info("Press 'q' to stop recording")
    force_mp3 = False

    if record_file_format != "mp3" and record_file_format != "auto":
        record_file_format = "mp3"  # default to mp3
        log.debug("Error: wrong codec supplied!. falling back to mp3")
        force_mp3 = True
    elif record_file_format == "auto":
        log.debug("Codec: fetching stream codec")
        codec = record_audio_auto_codec(target_url)
        if codec is None:
            record_file_format = "mp3"  # default to mp3
            force_mp3 = True
            log.debug("Error: could not detect codec. falling back to mp3")
        else:
            record_file_format = codec
            log.debug("Codec: found {}".format(codec))
    elif record_file_format == "mp3":
        # always save to mp3 to eliminate any runtime issues
        # it is better to leave it on libmp3lame
        force_mp3 = True

    if record_file_path and not os.path.exists(record_file_path):
        log.debug("filepath: {}".format(record_file_path))
        os.makedirs(record_file_path, exist_ok=True)

    elif not record_file_path:
        log.debug("filepath: fallback to default path")
        record_file_path = os.path.join(
            os.path.expanduser("~"), "Music/radioactive"
        )  # fallback path
        try:
            os.makedirs(record_file_path, exist_ok=True)
        except Exception as e:
            log.debug("{}".format(e))
            log.error("Could not make default directory")
            sys.exit(1)

    now = datetime.datetime.now()
    month_name = now.strftime("%b").upper()
    # Format AM/PM as 'AM' or 'PM'
    am_pm = now.strftime("%p")

    # format is : day-monthname-year@hour-minute-second-(AM/PM)
    formatted_date_time = now.strftime(f"%d-{month_name}-%Y@%I-%M-%S-{am_pm}")

    if not record_file_format.strip():
        record_file_format = "mp3"

    if not record_file:
        record_file = "{}-{}".format(
            curr_station_name.strip(), formatted_date_time
        ).replace(" ", "-")

    tmp_filename = f"{record_file}.{record_file_format}"
    outfile_path = os.path.join(record_file_path, tmp_filename)

    log.info(f"Recording will be saved as: \n{outfile_path}")

    record_audio_from_url(target_url, outfile_path, force_mp3, loglevel)


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
        expand=True,
        safe_box=True,
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
    # log.info("Your favorite station list is below")
    table = Table(
        show_header=True,
        header_style="bold magenta",
        min_width=85,
        safe_box=False,
        expand=True,
    )
    table.add_column("Station", justify="left")
    table.add_column("URL / UUID", justify="left")
    if len(alias.alias_map) > 0:
        for entry in alias.alias_map:
            table.add_row(entry["name"], entry["uuid_or_url"])
        print(table)
        log.info(f"Your favorite stations are saved in {alias.alias_path}")
    else:
        log.info("You have no favorite station list")


def handle_show_station_info():
    """Show important information regarding the current station"""
    global global_current_station_info
    custom_info = {}
    try:
        custom_info["name"] = global_current_station_info["name"]
        custom_info["uuid"] = global_current_station_info["stationuuid"]
        custom_info["url"] = global_current_station_info["url"]
        custom_info["website"] = global_current_station_info["homepage"]
        custom_info["country"] = global_current_station_info["country"]
        custom_info["language"] = global_current_station_info["language"]
        custom_info["tags"] = global_current_station_info["tags"]
        custom_info["codec"] = global_current_station_info["codec"]
        custom_info["bitrate"] = global_current_station_info["bitrate"]
        print(custom_info)
    except:
        log.error("No station information available")


def handle_add_station(alias):
    try:
        left = input("Enter station name:")
        right = input("Enter station stream-url or radio-browser uuid:")
    except EOFError:
        print()
        log.debug("Ctrl+D (EOF) detected. Exiting gracefully.")
        sys.exit(0)

    if left.strip() == "" or right.strip() == "":
        log.error("Empty inputs not allowed")
        sys.exit(1)
    alias.add_entry(left, right)
    log.info("New entry: {}={} added\n".format(left, right))
    sys.exit(0)


def handle_add_to_favorite(alias, station_name, station_uuid_url):
    try:
        response = alias.add_entry(station_name, station_uuid_url)
        if not response:
            try:
                user_input = input("Enter a different name: ")
            except EOFError:
                print()
                log.debug("Ctrl+D (EOF) detected. Exiting gracefully.")
                sys.exit(0)

            if user_input.strip() != "":
                response = alias.add_entry(user_input.strip(), station_uuid_url)
    except Exception as e:
        log.debug("Error: {}".format(e))
        log.error("Could not add to favorite. Already in list?")


def handle_station_uuid_play(handler, station_uuid):
    log.debug("Searching API for: {}".format(station_uuid))

    handler.play_by_station_uuid(station_uuid)

    log.debug("increased click count for: {}".format(station_uuid))

    handler.vote_for_uuid(station_uuid)
    try:
        station_name = handler.target_station["name"]
        station_url = handler.target_station["url"]
    except Exception as e:
        log.debug("{}".format(e))
        log.error("Something went wrong")
        sys.exit(1)

    return station_name, station_url


def check_sort_by_parameter(sort_by):
    accepted_parameters = [
        "name",
        "votes",
        "codec",
        "bitrate",
        "lastcheckok",
        "lastchecktime",
        "clickcount",
        "clicktrend",
        "random",
    ]

    if sort_by not in accepted_parameters:
        log.warning("Sort parameter is unknown. Falling back to 'name'")

        log.warning(
            "choose from: name,votes,codec,bitrate,lastcheckok,lastchecktime,clickcount,clicktrend,random"
        )
        return "name"
    return sort_by


def store_search_results_for_cycling(response, search_type="search"):
    """Store search/discovery results globally for cycle functionality"""
    global global_last_search_results
    
    if response is not None and len(response) > 0:
        global_last_search_results = response
        log.debug(f"Stored {len(global_last_search_results)} results from {search_type} for cycling")


def handle_search_stations(handler, station_name, limit, sort_by, filter_with):
    """Search for stations and store results globally for cycling"""
    log.debug("Searching API for: {}".format(station_name))

    response = handler.search_by_station_name(station_name, limit, sort_by, filter_with)
    
    # Store search results globally for cycle functionality
    store_search_results_for_cycling(response, "station search")
    
    return response


def handle_station_selection_menu(handler, last_station, alias):
    # Add a selection list here. first entry must be the last played station
    # try to fetch the last played station's information
    last_station_info = {}
    try:
        last_station_info = last_station.get_info()
    except Exception as e:
        log.debug("Error: {}".format(e))
        # no last station??
        pass

    # log.info("You can search for a station on internet using the --search option")
    title = "Please select a station from your favorite list:"
    station_selection_names = []
    station_selection_urls = []

    # add last played station first
    if last_station_info:
        station_selection_names.append(
            f"{last_station_info['name'].strip()} (last played station)"
        )
        try:
            station_selection_urls.append(last_station_info["stationuuid"])
        except Exception as e:
            log.debug("Error: {}".format(e))
            station_selection_urls.append(last_station_info["uuid_or_url"])

    fav_stations = alias.alias_map
    for entry in fav_stations:
        station_selection_names.append(entry["name"].strip())
        station_selection_urls.append(entry["uuid_or_url"])

    options = station_selection_names
    if len(options) == 0:
        log.info(
            f"{RED_COLOR}No stations to play. please search for a station first!{END_COLOR}"
        )
        sys.exit(0)

    _, index = pick(options, title, indicator="-->")

    # check if there is direct URL or just UUID
    station_option_url = station_selection_urls[index]
    station_name = station_selection_names[index].replace("(last played station)", "")

    if station_option_url.find("://") != -1:
        # direct URL
        station_url = station_option_url
        return station_name, station_url

    else:
        # UUID
        station_uuid = station_option_url
        return handle_station_uuid_play(handler, station_uuid)


def handle_save_last_station(last_station, station_name, station_url):
    last_station = Last_station()

    last_played_station = {}
    last_played_station["name"] = station_name
    last_played_station["uuid_or_url"] = station_url

    log.debug(f"Saving the current station: {last_played_station}")
    last_station.save_info(last_played_station)


def handle_listen_keypress(
    alias,
    player,
    handler,
    last_station,
    target_url,
    station_name,
    station_url,
    record_file_path,
    record_file,
    record_file_format,
    loglevel,
    volume,
):
    log.info("Press '?' to see available commands\n")
    
    # Keep track of current station info for potential updates
    current_target_url = target_url
    current_station_name = station_name
    current_station_url = station_url
    current_player = player  # Track current player instance
    
    while True:
        try:
            user_input = input("Enter a command to perform an action: ")
        except EOFError:
            print()
            log.debug("Ctrl+D (EOF) detected. Exiting gracefully.")
            kill_background_ffplays()
            sys.exit(0)

        if user_input in ["r", "R", "record"]:
            handle_record(
                current_target_url,
                current_station_name,
                record_file_path,
                record_file,
                record_file_format,
                loglevel,
            )
        elif user_input in ["rf", "RF", "recordfile"]:
            # if no filename is provided try to auto detect
            # else if ".mp3" is provided, use libmp3lame to force write to mp3
            try:
                user_input = input("Enter output filename: ")
            except EOFError:
                print()
                log.debug("Ctrl+D (EOF) detected. Exiting gracefully.")
                kill_background_ffplays()
                sys.exit(0)

            # try to get extension from filename
            try:
                file_name, file_ext = user_input.split(".")
                if file_ext == "mp3":
                    log.debug("codec: force mp3")
                    # overwrite original codec with "mp3"
                    record_file_format = "mp3"
                else:
                    log.warning("You can only specify mp3 as file extension.\n")
                    log.warning(
                        "Do not provide any extension to autodetect the codec.\n"
                    )
            except:
                file_name = user_input

            if user_input.strip() != "":
                handle_record(
                    current_target_url,
                    current_station_name,
                    record_file_path,
                    file_name,
                    record_file_format,
                    loglevel,
                )
        elif user_input in ["i", "I", "info"]:
            handle_show_station_info()

        elif user_input in ["f", "F", "fav"]:
            handle_add_to_favorite(alias, current_station_name, current_station_url)

        elif user_input in ["s", "S", "search"]:
            # New search functionality
            log.info("Searching for new stations...")
            log.info("Tip: You can search by station name, genre, or any keyword")
            new_station_name, new_target_url, new_player = handle_runtime_search_and_switch(
                handler, current_player, alias, last_station, loglevel, volume
            )
            
            # Update current station info if a new station was selected
            if new_station_name and new_target_url:
                current_station_name = new_station_name
                current_target_url = new_target_url
                current_station_url = new_target_url
                # Update player instance if a new one was created (FFplay case)
                if new_player:
                    current_player = new_player
                    log.debug("Updated to new player instance")
                log.info(f"Now playing: {current_station_name}")

        elif user_input in ["c", "C", "cycle"]:
            # Cycle through last search results
            log.info("Cycling through previous search results...")
            new_station_name, new_target_url, new_player = handle_runtime_cycle_stations(
                handler, current_player, alias, last_station, loglevel, volume
            )
            
            # Update current station info if a new station was selected
            if new_station_name and new_target_url:
                current_station_name = new_station_name
                current_target_url = new_target_url
                current_station_url = new_target_url
                # Update player instance if a new one was created (FFplay case)
                if new_player:
                    current_player = new_player
                    log.debug("Updated to new player instance")
                log.info(f"Now playing: {current_station_name}")

        elif user_input in ["q", "Q", "quit"]:
            # kill_background_ffplays()
            current_player.stop()
            sys.exit(0)
        elif user_input in ["w", "W", "list"]:
            alias.generate_map()
            handle_favorite_table(alias)
        elif user_input in ["t", "T", "track"]:
            handle_fetch_song_title(current_target_url)
        elif user_input in ["p", "P"]:
            # toggle the player (start/stop)
            current_player.toggle()
            # TODO: toggle the player

        elif user_input in ["h", "H", "?", "help"]:
            log.info("p: Play/Pause current station")
            log.info("s/search: Search and switch to new station")
            log.info("c/cycle: Choose different station from last search")
            log.info("t/track: Current track info")
            log.info("i/info: Station information")
            log.info("r/record: Record a station")
            log.info("rf/recordfile: Specify a filename for the recording")
            log.info("f/fav: Add station to favorite list")
            log.info("w/list: Show favorite stations")
            log.info("h/help/?: Show this help message")
            log.info("q/quit: Quit radioactive")


def handle_current_play_panel(curr_station_name=""):
    panel_station_name = Text(curr_station_name, justify="center")

    station_panel = Panel(panel_station_name, title="[blink]:radio:[/blink]", width=85)
    console = Console()
    console.print(station_panel)


def handle_user_choice_from_search_result(handler, response):
    global global_current_station_info

    if not response:
        log.debug("No result found!")
        sys.exit(0)
    if len(response) == 1:
        # single station found
        log.debug("Exactly one result found")

        try:
            user_input = input("Want to play this station? Y/N: ")
        except EOFError:
            print()
            sys.exit(0)

        if user_input in ["y", "Y"]:
            log.debug("Playing UUID from single response")
            global_current_station_info = response[0]

            return handle_station_uuid_play(handler, response[0]["stationuuid"])
        else:
            log.debug("Quitting")
            sys.exit(0)
    else:
        # multiple station
        log.debug("Asking for user input")

        try:
            log.info("Type 'r' to play a random station")
            user_input = input("Type the result ID to play: ")
        except EOFError:
            print()
            log.info("Exiting")
            log.debug("EOF reached, quitting")
            sys.exit(0)

        try:
            if user_input in ["r", "R", "random"]:
                # pick a random integer withing range
                user_input = randint(1, len(response) - 1)
                log.debug(f"Radom station id: {user_input}")
            # elif user_input in ["f", "F", "fuzzy"]:
            # fuzzy find all the stations, and return the selected station id
            # user_input = fuzzy_find(response)

            user_input = int(user_input) - 1  # because ID starts from 1
            if user_input in range(0, len(response)):
                target_response = response[user_input]
                log.debug("Selected: {}".format(target_response))
                # log.info("UUID: {}".format(target_response["stationuuid"]))

                # saving global info
                global_current_station_info = target_response

                return handle_station_uuid_play(handler, target_response["stationuuid"])
            else:
                log.error("Please enter an ID within the range")
                sys.exit(1)
        except:
            log.err("Please enter an valid ID number")
            sys.exit(1)


def handle_direct_play(alias, station_name_or_url=""):
    """Play a station directly with UUID or direct stream URL"""
    if "://" in station_name_or_url.strip():
        log.debug("Direct play: URL provided")
        # stream URL
        # call using URL with no station name N/A
        # let's attempt to get station name from url headers
        # station_name = handle_station_name_from_headers(station_name_or_url)
        station_name = handle_get_station_name_from_metadata(station_name_or_url)
        return station_name, station_name_or_url
    else:
        log.debug("Direct play: station name provided")
        # station name from fav list
        # search for the station in fav list and return name and url

        response = alias.search(station_name_or_url)
        if not response:
            log.error("No station found on your favorite list with the name")
            sys.exit(1)
        else:
            log.debug("Direct play: {}".format(response))
            return response["name"], response["uuid_or_url"]


def handle_play_last_station(last_station):
    station_obj = last_station.get_info()
    return station_obj["name"], station_obj["uuid_or_url"]


def handle_runtime_search_and_switch(handler, player, alias, last_station, loglevel, volume):
    """Handle runtime search for new stations and switch to selected station"""
    global global_last_search_results
    
    try:
        search_term = input("Enter station name to search: ")
    except EOFError:
        print()
        log.debug("Ctrl+D (EOF) detected during search input.")
        return None, None, None

    if search_term.strip() == "":
        log.info("Search cancelled")
        return None, None, None

    log.info(f"Searching for: {search_term}")
    
    # Use default values from config for search parameters
    # These could be made configurable in the future
    limit = 100
    sort_by = "votes"
    filter_with = "none"
    
    try:
        # Search for stations
        response = handle_search_stations(handler, search_term, limit, sort_by, filter_with)
        
        if response is not None and len(response) > 0:
            # Store search results for cycle functionality
            global_last_search_results = response
            log.debug(f"Stored {len(global_last_search_results)} search results for cycling")
            
            # Let user select from search results
            new_station_name, new_target_url = handle_user_choice_from_search_result(handler, response)
            
            if new_station_name and new_target_url:
                return switch_to_new_station(player, new_station_name, new_target_url, last_station, loglevel, volume)
            
    except Exception as e:
        log.error(f"Error during search: {e}")
        log.debug(f"Search error details: {str(e)}")
        log.info("Continuing with current station...")
    
    return None, None, None


def handle_runtime_cycle_stations(handler, player, alias, last_station, loglevel, volume):
    """Cycle through last search results to pick a different station"""
    global global_last_search_results
    
    log.debug(f"Cycle: Found {len(global_last_search_results)} stored results")
    
    if not global_last_search_results:
        log.info("No previous search results available. Use 's/search' first.")
        return None, None, None
    
    log.info(f"Showing {len(global_last_search_results)} stations from previous search:")
    
    try:
        # Show the stored search results table again
        from radioactive.handler import print_table
        print_table(global_last_search_results, 
                   ["Station:name@30", "Country:country@20", "Tags:tags@20"], 
                   "votes", "none")
        
        # Let user select from previous results
        new_station_name, new_target_url = handle_user_choice_from_search_result(handler, global_last_search_results)
        
        if new_station_name and new_target_url:
            return switch_to_new_station(player, new_station_name, new_target_url, last_station, loglevel, volume)
            
    except Exception as e:
        log.error(f"Error during cycle: {e}")
        log.debug(f"Cycle error details: {str(e)}")
        log.info("Continuing with current station...")
    
    return None, None, None


def switch_to_new_station(player, new_station_name, new_target_url, last_station, loglevel, volume):
    """Helper function to switch to a new station regardless of player type"""
    try:
        # Stop current player and ensure it's fully stopped
        log.info("Switching to new station...")
        
        # Force stop current player
        if player and hasattr(player, 'stop'):
            player.stop()
        
        # Kill any background ffplay processes to prevent simultaneous playback
        kill_background_ffplays()
        
        # Small delay to ensure cleanup
        from time import sleep
        sleep(0.5)
        
        # Handle different player types
        if hasattr(player, 'program_name'):
            if player.program_name == "ffplay":
                # FFplay needs to be reinitialized - return new instance
                from radioactive.ffplay import Ffplay
                new_player = Ffplay(new_target_url, volume, loglevel)
                log.debug("FFplay reinitialized for new station")
                
                # Save as last station
                handle_save_last_station(last_station, new_station_name, new_target_url)
                
                # Show new station panel
                handle_current_play_panel(new_station_name)
                
                # Return the new player instance along with station info
                return new_station_name, new_target_url, new_player
                
            elif player.program_name == "vlc":
                # VLC has start method
                player.url = new_target_url
                player.start(new_target_url)
                
            elif player.program_name == "mpv":
                # MPV has start method  
                player.url = new_target_url
                player.start(new_target_url)
        else:
            # Fallback - try the start method for other players
            if hasattr(player, 'url'):
                player.url = new_target_url
            if hasattr(player, 'start'):
                player.start(new_target_url)
            else:
                log.warning("Could not restart player - player type not recognized")
                return new_station_name, new_target_url, None
        
        # Save as last station
        handle_save_last_station(last_station, new_station_name, new_target_url)
        
        # Show new station panel
        handle_current_play_panel(new_station_name)
        
        # Return None for player if no new instance was created
        return new_station_name, new_target_url, None
        
    except Exception as e:
        log.error(f"Error switching station: {e}")
        log.debug(f"Detailed error: {str(e)}")
        return None, None, None


# uses ffprobe to fetch station name
def handle_get_station_name_from_metadata(url):
    """Get ICY metadata from ffprobe"""
    log.info("Fetching the station name")
    log.debug("Attempting to retrieve station name from: {}".format(url))
    # Run ffprobe command and capture the metadata
    cmd = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_entries",
        "format=icy",
        url,
    ]
    station_name = "Unknown Station"

    try:
        output = subprocess.check_output(cmd).decode("utf-8")
        data = json.loads(output)
        log.debug(f"station info: {data}")

        # Extract the station name (icy-name) if available
        station_name = (
            data.get("format", {}).get("tags", {}).get("icy-name", "Unknown Station")
        )
    except:
        log.error("Could not fetch the station name")

    return station_name


# uses requests module to fetch station name [deprecated]
def handle_station_name_from_headers(url):
    # Get headers from URL so that we can get radio station
    log.info("Fetching the station name")
    log.debug("Attempting to retrieve station name from: {}".format(url))
    station_name = "Unknown Station"
    try:
        # sync call, with timeout
        response = requests.get(url, timeout=5)
        if response.status_code == requests.codes.ok:
            if response.headers.get("Icy-Name"):
                station_name = response.headers.get("Icy-Name")
            else:
                log.error("Station name not found")
        else:
            log.debug("Response code received is: {}".format(response.status_code()))
    except Exception as e:
        # except requests.HTTPError and requests.exceptions.ReadTimeout as e:
        log.error("Could not fetch the station name")
        log.debug(
            """An error occurred: {}
    The response code was {}""".format(
                e, e.errno
            )
        )
    return station_name


def handle_play_random_station(alias):
    """Select a random station from favorite menu"""
    log.debug("playing a random station")
    alias_map = alias.alias_map
    index = randint(0, len(alias_map) - 1)
    station = alias_map[index]
    return station["name"], station["uuid_or_url"]
