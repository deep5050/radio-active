"""
Module for filtering radio station results based on various criteria.
"""

import sys
from typing import Any, Dict, List, Union

from zenlog import log


def _filter_entries_by_key(
    data: List[Dict[str, Any]], filter_param: str, key: str
) -> List[Dict[str, Any]]:
    """
    Filter list of dictionaries by a string key using inclusion (=) or exclusion (!=).
    """
    log.debug(f"filter: {filter_param}")

    filtered_entries = []

    for entry in data:
        value = entry.get(key)
        # Ensure value is a string for comparison
        if value is None:
            continue

        str_value = str(value)
        if str_value == "":
            continue

        if "!=" in filter_param:
            # Handle exclusion
            # Splitting safely to avoid index errors
            parts = filter_param.split("!=")
            if len(parts) > 1:
                exclusion_values = parts[1].split(",")
                if all(
                    exclusion_value.lower() not in str_value.lower()
                    for exclusion_value in exclusion_values
                ):
                    filtered_entries.append(entry)

        elif "=" in filter_param:
            # Handle inclusion
            parts = filter_param.split("=")
            if len(parts) > 1:
                inclusion_values = parts[1].split(",")
                if any(
                    inclusion_value.lower() in str_value.lower()
                    for inclusion_value in inclusion_values
                ):
                    filtered_entries.append(entry)

    return filtered_entries


def _filter_entries_by_numeric_key(
    data: List[Dict[str, Any]], filter_param: str, key: str
) -> List[Dict[str, Any]]:
    """
    Filter list of dictionaries by a numeric key.
    Supports <, >, and = operators.
    """
    filtered_entries = []

    try:
        # Split logic needs to be robust.
        # Expected format: keyOPvalue e.g. votes>100
        # We know the key, so we can split by key
        parts = filter_param.split(key)
        if len(parts) < 2:
            log.warning(f"Invalid filter format: {filter_param}")
            return data

        param_part = parts[1]  # portion after the key name e.g. >100, =50
        if not param_part:
            return data

        filter_operator = param_part[0]  # operator part
        filter_value_str = param_part[1:]  # value part

        if not filter_value_str:
            log.warning(f"No value provided for filter: {filter_param}")
            return data

        filter_value = int(filter_value_str)

        for entry in data:
            val = entry.get(key)
            if val is not None:
                try:
                    # Convert to int, default to 0 if fails
                    int_val = int(val)
                except (ValueError, TypeError):
                    continue

                if filter_operator not in [">", "<", "="]:
                    log.warning(f"Unsupported filter operator: {filter_operator}")
                    return data

                if filter_operator == "<" and int_val < filter_value:
                    filtered_entries.append(entry)
                elif filter_operator == ">" and int_val > filter_value:
                    filtered_entries.append(entry)
                elif filter_operator == "=" and int_val == filter_value:
                    filtered_entries.append(entry)

    except ValueError:
        log.error(f"Invalid numeric filter value for {key}: {filter_param}")
        sys.exit(1)
    except Exception as e:
        log.error(f"Error filtering by numeric key {key}: {e}")
        sys.exit(1)

    return filtered_entries


# allowed string string filters
def _filter_entries_by_name(data: List[Dict], filter_param: str) -> List[Dict]:
    return _filter_entries_by_key(data, filter_param, key="name")


def _filter_entries_by_language(data: List[Dict], filter_param: str) -> List[Dict]:
    return _filter_entries_by_key(data, filter_param, key="language")


def _filter_entries_by_country(data: List[Dict], filter_param: str) -> List[Dict]:
    return _filter_entries_by_key(data, filter_param, key="countrycode")


def _filter_entries_by_tags(data: List[Dict], filter_param: str) -> List[Dict]:
    return _filter_entries_by_key(data, filter_param, key="tags")


def _filter_entries_by_codec(data: List[Dict], filter_param: str) -> List[Dict]:
    return _filter_entries_by_key(data, filter_param, key="codec")


# allowed numeric filters
def _filter_entries_by_votes(data: List[Dict], filter_param: str) -> List[Dict]:
    return _filter_entries_by_numeric_key(data, filter_param, key="votes")


def _filter_entries_by_bitrate(data: List[Dict], filter_param: str) -> List[Dict]:
    return _filter_entries_by_numeric_key(data, filter_param, key="bitrate")


def _filter_entries_by_clickcount(data: List[Dict], filter_param: str) -> List[Dict]:
    return _filter_entries_by_numeric_key(data, filter_param, key="clickcount")


# top level filter function
def _filter_results(data: List[Dict], expression: str) -> List[Dict]:
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
        log.warning(f"Unknown filter expression: {expression}, not filtering!")
        return data


# Top most function for multiple filtering expressions with '&'
def filter_expressions(
    data: List[Dict[str, Any]], input_expression: str
) -> List[Dict[str, Any]]:
    """
    Filter the list of stations based on the input expression.
    Supports multiple filters separated by '&'.
    """
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
