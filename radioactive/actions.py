"""
Core logical actions for radio-active.
"""

import datetime
import json
import os
import subprocess
import sys
from random import randint
from typing import Any, Dict, List, Optional, Tuple, Union

import requests
from zenlog import log

from radioactive.recorder import record_audio_auto_codec, record_audio_from_url
from radioactive.last_station import Last_station


def handle_fetch_song_title(url: str) -> None:
    """Fetch currently playing track information"""
    log.info("Fetching the current track info")
    log.debug(f"Attempting to retrieve track info from: {url}")
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
    except Exception:
        log.error("Error while fetching the track name")

    if track_name != "":
        log.info(f"🎶: {track_name}")
    else:
        log.error("No track information available")


def handle_record(
    target_url: str,
    curr_station_name: str,
    record_file_path: str,
    record_file: str,
    record_file_format: str,  # auto/mp3
    loglevel: str,
) -> None:
    """
    Handle audio recording logic.
    """
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
            log.debug(f"Codec: found {codec}")
    elif record_file_format == "mp3":
        # always save to mp3 to eliminate any runtime issues
        # it is better to leave it on libmp3lame
        force_mp3 = True

    if record_file_path and not os.path.exists(record_file_path):
        log.debug(f"filepath: {record_file_path}")
        os.makedirs(record_file_path, exist_ok=True)

    elif not record_file_path:
        log.debug("filepath: fallback to default path")
        record_file_path = os.path.join(
            os.path.expanduser("~"), "Music/radioactive"
        )  # fallback path
        try:
            os.makedirs(record_file_path, exist_ok=True)
        except Exception as e:
            log.debug(f"{e}")
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


def handle_add_station(alias) -> None:
    """Add a new station to favorites via user input."""
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


def handle_add_to_favorite(alias, station_name: str, station_uuid_url: str) -> None:
    """Add the current station to favorites."""
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
        log.debug(f"Error: {e}")
        log.error("Could not add to favorite. Already in list?")


def handle_save_last_station(last_station, station_name: str, station_url: str) -> None:
    """Save the last played station."""
    # last_station = Last_station() # Provided as arg now
    
    last_played_station = {}
    last_played_station["name"] = station_name
    last_played_station["uuid_or_url"] = station_url

    log.debug(f"Saving the current station: {last_played_station}")
    last_station.save_info(last_played_station)


def check_sort_by_parameter(sort_by: str) -> str:
    """Validate and return the sort parameter."""
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


def handle_search_stations(
    handler, 
    station_name: str, 
    limit: int, 
    sort_by: str, 
    filter_with: str
) -> Any:
    """Wrapper to search stations by name."""
    log.debug(f"Searching API for: {station_name}")
    return handler.search_by_station_name(station_name, limit, sort_by, filter_with)


def handle_station_uuid_play(handler, station_uuid: str) -> Tuple[str, str]:
    """Play a station by UUID and register a vote."""
    log.debug(f"Searching API for: {station_uuid}")

    handler.play_by_station_uuid(station_uuid)

    log.debug(f"increased click count for: {station_uuid}")

    handler.vote_for_uuid(station_uuid)
    try:
        station_name = handler.target_station["name"]
        station_url = handler.target_station["url"]
    except Exception as e:
        log.debug(f"{e}")
        log.error("Something went wrong")
        sys.exit(1)

    return station_name, station_url


def handle_direct_play(alias, station_name_or_url: str = "") -> Tuple[str, str]:
    """Play a station directly with UUID or direct stream URL."""
    if "://" in station_name_or_url.strip():
        log.debug("Direct play: URL provided")
        # stream URL
        # call using URL with no station name N/A
        # attempt to get station name from metadata
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
            log.debug(f"Direct play: {response}")
            return response["name"], response["uuid_or_url"]


def handle_play_last_station(last_station) -> Tuple[str, str]:
    """Play the last played station."""
    station_obj = last_station.get_info()
    return station_obj["name"], station_obj["uuid_or_url"]


def handle_get_station_name_from_metadata(url: str) -> str:
    """Get ICY metadata from ffprobe to find station name."""
    log.info("Fetching the station name")
    log.debug(f"Attempting to retrieve station name from: {url}")
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
    except Exception:
        log.error("Could not fetch the station name")

    return station_name


def handle_station_name_from_headers(url: str) -> str:
    """
    Get headers from URL to find station name (deprecated).
    """
    log.info("Fetching the station name")
    log.debug(f"Attempting to retrieve station name from: {url}")
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
            log.debug(f"Response code received is: {response.status_code}")
    except Exception as e:
        log.error("Could not fetch the station name")
        log.debug(f"An error occurred: {e}")
    return station_name


def handle_play_random_station(alias) -> Tuple[str, str]:
    """Select a random station from favorite menu."""
    log.debug("playing a random station")
    alias_map = alias.alias_map
    if not alias_map:
        log.error("No favorite stations found")
        sys.exit(1)
        
    index = randint(0, len(alias_map) - 1)
    station = alias_map[index]
    return station["name"], station["uuid_or_url"]
