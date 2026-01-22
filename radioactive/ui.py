"""
UI components for radio-active using Rich.
"""

from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from zenlog import log

# Global variable to store current station info for display
# This is shared state, ideally should be managed better, but keeping for compatibility
global_current_station_info = {}


def handle_welcome_screen() -> None:
    """Print the welcome screen panel."""
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


def handle_update_screen(app) -> None:
    """
    Check for updates and print a message if available.
    
    Args:
        app: The App instance to check for updates.
    """
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


def handle_favorite_table(alias) -> None:
    """
    Print the user's favorite list in a table.
    
    Args:
        alias: The Alias instance containing the favorite map.
    """
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


def handle_show_station_info() -> None:
    """Show important information regarding the current station."""
    # pylint: disable=global-statement
    global global_current_station_info
    custom_info = {}
    try:
        custom_info["name"] = global_current_station_info.get("name")
        custom_info["uuid"] = global_current_station_info.get("stationuuid")
        custom_info["url"] = global_current_station_info.get("url")
        custom_info["website"] = global_current_station_info.get("homepage")
        custom_info["country"] = global_current_station_info.get("country")
        custom_info["language"] = global_current_station_info.get("language")
        custom_info["tags"] = global_current_station_info.get("tags")
        custom_info["codec"] = global_current_station_info.get("codec")
        custom_info["bitrate"] = global_current_station_info.get("bitrate")
        print(custom_info)
    except Exception as e:
        log.error(f"No station information available: {e}")


def handle_current_play_panel(curr_station_name: str = "") -> None:
    """
    Print the currently playing station panel.
    
    Args:
        curr_station_name (str): Name of the station.
    """
    panel_station_name = Text(curr_station_name, justify="center")

    station_panel = Panel(panel_station_name, title="[blink]:radio:[/blink]", width=85)
    console = Console()
    console.print(station_panel)


def set_global_station_info(info: dict) -> None:
    """Helper to update global station info from other modules."""
    global global_current_station_info
    global_current_station_info = info
