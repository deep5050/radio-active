from zenlog import log

from radioactive.args import Parser


def parse_options():
    parser = Parser()
    args = parser.parse()
    options = {}
    # ----------------- all the args ------------- #
    options["show_help_table"] = args.help
    options["version"] = args.version
    options["loglevel"] = args.log_level
    options["search_station_name"] = args.search_station_name
    options["direct_play"] = args.direct_play
    options["play_last_station"] = args.play_last_station

    options["search_station_uuid"] = args.search_station_uuid
    options["sort_by"] = args.stations_sort_by
    options["discover_country_code"] = args.discover_country_code
    options["discover_state"] = args.discover_state
    options["discover_language"] = args.discover_language
    options["discover_tag"] = args.discover_tag

    limit = args.limit
    options["limit"] = int(limit) if limit else 100
    log.debug("limit is set to: {}".format(limit))

    options["add_station"] = args.new_station
    options["add_to_favorite"] = args.add_to_favorite
    options["show_favorite_list"] = args.show_favorite_list

    options["flush_fav_list"] = args.flush
    options["kill_ffplays"] = args.kill_ffplays

    options["record_stream"] = args.record_stream
    options["record_file"] = args.record_file
    options["record_file_format"] = args.record_file_format
    options["record_file_path"] = args.record_file_path

    options["target_url"] = ""
    options["volume"] = args.volume

    return options
