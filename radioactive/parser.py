from zenlog import log

from radioactive.args import Parser


def parse_options():
    parser = Parser()
    args = parser.parse()
    options = {}
    # ----------------- all the args ------------- #
    options["version"] = args.version
    options["show_help_table"] = args.help
    options["loglevel"] = args.log_level

    # check log levels
    if options["loglevel"] in ["info", "error", "warning", "debug"]:
        log.level(options["loglevel"])
    else:
        log.level("info")
        log.warning("Correct log levels are: error,warning,info(default),debug")

    # check is limit is a valid integer
    limit = args.limit
    options["limit"] = int(limit) if limit else 100
    log.debug("limit is set to: {}".format(limit))

    options["search_station_name"] = args.search_station_name
    options["search_station_uuid"] = args.search_station_uuid

    options["play_last_station"] = args.play_last_station
    options["direct_play"] = args.direct_play
    options["play_random"] = args.play_random_station

    options["sort_by"] = args.stations_sort_by

    options["discover_country_code"] = args.discover_country_code
    options["discover_state"] = args.discover_state
    options["discover_language"] = args.discover_language
    options["discover_tag"] = args.discover_tag

    options["add_station"] = args.new_station

    options["show_favorite_list"] = args.show_favorite_list
    options["add_to_favorite"] = args.add_to_favorite
    options["flush_fav_list"] = args.flush
    options["remove_fav_stations"] = args.remove_fav_stations

    options["kill_ffplays"] = args.kill_ffplays

    options["record_stream"] = args.record_stream
    options["record_file"] = args.record_file
    options["record_file_format"] = args.record_file_format
    options["record_file_path"] = args.record_file_path

    options["target_url"] = ""
    options["volume"] = args.volume
    options["audio_player"] = args.audio_player

    return options
