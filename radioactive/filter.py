import sys

from zenlog import log


# function to filter strings
def _filter_entries_by_key(data, filter_param, key):
    log.debug(f"filter: {filter_param}")

    filtered_entries = []

    for entry in data:
        value = entry.get(key)

        if value is not None and value != "":
            if "!=" in filter_param:
                # Handle exclusion
                exclusion_values = filter_param.split("!=")[1].split(",")

                if all(
                    exclusion_value.lower() not in value.lower()
                    for exclusion_value in exclusion_values
                ):
                    filtered_entries.append(entry)

            elif "=" in filter_param:
                # Handle inclusion
                inclusion_values = filter_param.split("=")[1].split(",")

                if any(
                    inclusion_value.lower() in value.lower()
                    for inclusion_value in inclusion_values
                ):
                    filtered_entries.append(entry)

    return filtered_entries


# function to filter numeric values
def _filter_entries_by_numeric_key(data, filter_param, key):
    filtered_entries = []

    # filter_key = filter_param.split(key)[0]  # most left hand of the expression
    filter_param = filter_param.split(key)[1]  # portion after the operator
    filter_operator = filter_param[0]  # operator part
    filter_value = int(filter_param[1:])  # value part
    # log.debug(f"filter: parameter:{filter_param}")

    for entry in data:
        value = int(entry.get(key))

        if value is not None:
            try:
                if filter_operator not in [">", "<", "="]:
                    log.warning("Unsupported filter operator, not filtering !!")
                    return data
                if filter_operator == "<" and value < filter_value:
                    filtered_entries.append(entry)
                elif filter_operator == ">" and value > filter_value:
                    filtered_entries.append(entry)
                elif filter_operator == "=" and value == filter_value:
                    filtered_entries.append(entry)

            except ValueError:
                log.error(f"Invalid filter value for {key}: {filter_param}")
                sys.exit(1)

    return filtered_entries


# allowed string string filters
def _filter_entries_by_name(data, filter_param):
    return _filter_entries_by_key(data, filter_param, key="name")


def _filter_entries_by_language(data, filter_param):
    return _filter_entries_by_key(data, filter_param, key="language")


def _filter_entries_by_country(data, filter_param):
    return _filter_entries_by_key(data, filter_param, key="countrycode")


def _filter_entries_by_tags(data, filter_param):
    return _filter_entries_by_key(data, filter_param, key="tags")


def _filter_entries_by_codec(data, filter_param):
    return _filter_entries_by_key(data, filter_param, key="codec")


# allowed numeric filters
def _filter_entries_by_votes(data, filter_param):
    return _filter_entries_by_numeric_key(data, filter_param, key="votes")


def _filter_entries_by_bitrate(data, filter_param):
    return _filter_entries_by_numeric_key(data, filter_param, key="bitrate")


def _filter_entries_by_clickcount(data, filter_param):
    return _filter_entries_by_numeric_key(data, filter_param, key="clickcount")


# top level filter function
def _filter_results(data, expression):
    log.debug(f"Filter exp: {expression}")
    if not data:
        log.error("Empty results")
        sys.exit(0)

    if "name" in expression:
        return _filter_entries_by_name(data, expression)
    elif "language" in expression:
        return _filter_entries_by_language(data, expression)
    elif "country" in expression:
        return _filter_entries_by_country(data, expression)
    elif "tags" in expression:
        return _filter_entries_by_tags(data, expression)
    elif "codec" in expression:
        return _filter_entries_by_codec(data, expression)
    elif "bitrate" in expression:
        return _filter_entries_by_bitrate(data, expression)
    elif "clickcount" in expression:
        return _filter_entries_by_clickcount(data, expression)
    elif "votes" in expression:
        return _filter_entries_by_votes(data, expression)
    else:
        log.warning("Unknown filter expression, not filtering!")
        return data


# Top most function for multiple filtering expressions with '&'
# NOTE: it will filter maintaining the order you provided on the CLI


def filter_expressions(data, input_expression):
    log.info(
        "Setting a higher value for the --limit parameter is preferable when filtering stations."
    )
    if "&" in input_expression:
        log.debug("filter: multiple expressions found")
        expression_parts = input_expression.split("&")

        for expression in expression_parts:
            if data:
                data = _filter_results(data, expression)
        return data

    else:
        return _filter_results(data, input_expression)
