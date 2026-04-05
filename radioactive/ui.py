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
        local_version = app.get_version()
        remote_version = app.get_remote_version()

        update_msg = (
            f"\t[blink]An update available, run [green][italic]pip install radio-active=="
            + remote_version
            + f"[/italic][/green][/blink]\n"
        )

        # Add release notes for all missing versions if available
        release_notes = app.get_release_notes(local_version, remote_version)
        if release_notes:
            update_msg += f"\n[bold yellow]What's new since v{local_version}:[/bold yellow]\n{release_notes}"
        else:
            update_msg += f"\nSee all changes: https://github.com/deep5050/radio-active/blob/main/CHANGELOG.md"

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


def handle_history_table(history) -> None:
    """
    Print the user's history list in a table.

    Args:
        history: The History instance containing the history list.
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

    if len(history.history_list) > 0:
        for entry in history.history_list:
            table.add_row(entry["name"], entry["uuid_or_url"])
        print(table)
        log.info(f"Your history is saved in {history.history_path}")
    else:
        log.info("You have no history")


def handle_show_station_info() -> None:
    """Show important information regarding the current station in an alternate screen (Modal)."""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table

        console = Console()
        with console.screen():
            table = Table(box=None, padding=(0, 2), show_header=False)
            table.add_column("Property", style="cyan", justify="left")
            table.add_column("Value", style="white")

            # Map internal keys to display labels
            fields = [
                ("Name", "name"),
                ("UUID", "stationuuid"),
                ("Stream URL", "url"),
                ("Website", "homepage"),
                ("Country", "country"),
                ("Language", "language"),
                ("Tags", "tags"),
                ("Codec", "codec"),
                ("Bitrate", "bitrate"),
            ]

            for label, key in fields:
                val = str(global_current_station_info.get(key, "N/A"))
                if val.strip() == "" or val == "None":
                    val = "N/A"
                table.add_row(f"{label}:", val)

            info_panel = Panel(
                table,
                title="[bold magenta]:radio: Station Information[/bold magenta]",
                subtitle="[blink]Press Enter to return[/blink]",
                border_style="magenta",
                padding=(1, 4),
                expand=False,
            )

            console.print("\n" * 3)
            console.print(info_panel, justify="center")

            try:
                console.input()
            except (EOFError, KeyboardInterrupt):
                pass

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


def get_global_station_info() -> dict:
    """Helper to get global station info."""
    return global_current_station_info
