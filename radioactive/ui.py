"""
UI components for radio-active using Rich.
"""

from typing import Any, Optional

from rich import print
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from zenlog import log

# Global variable to store current station info for display
# This is shared state, ideally should be managed better, but keeping for compatibility
global_current_station_info = {}

# Persistent Live display elements
_console = Console()
_live_display = None

# UI State components
_app_banner = None
_station_banner = None
_prompt_renderable = None


def _get_banner_panel(curr_station_name: str) -> Panel:
    """Internal helper to create the banner panel."""
    panel_station_name = Text(curr_station_name, justify="center")
    return Panel(
        panel_station_name, title=":radio: Current Station", width=80, expand=False
    )


def _get_welcome_panel() -> Panel:
    """Internal helper to create the app banner."""
    return Panel(
        """
        :radio: Play any radios around the globe right from this Terminal [yellow]:zap:[/yellow]!
        :smile: Author: Dipankar Pal
        :question: Type '?' for help, any string to search favorites/history
        :x: Press Ctrl+C to quit
        """,
        title="[b]RADIOACTIVE[/b]",
        width=80,
        expand=False,
        safe_box=True,
    )


def _get_composite_renderable():
    """Combine all active UI components into a single Group."""
    components = []
    if _app_banner:
        components.append(_app_banner)
    if _station_banner:
        components.append(_station_banner)
    if _prompt_renderable:
        components.append(_prompt_renderable)

    return Group(*components)


def refresh_live_display():
    """Update the persistent live display with the current composite renderable."""
    if _live_display:
        _live_display.update(_get_composite_renderable(), refresh=True)


def handle_welcome_screen() -> None:
    """
    Prepare the app banner for the playback UI.

    Do not start Rich Live here: interactive flows (e.g. ``pick`` for favorites)
    use curses and break Live's cursor accounting. Live starts in
    handle_current_play_panel when the main TUI is shown.
    """
    global _app_banner
    _app_banner = _get_welcome_panel()
    if _live_display is not None:
        refresh_live_display()


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
            width=80,
            expand=False,
        )
        _console.print(update_panel)
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
        width=80,
        safe_box=False,
        expand=False,
    )
    table.add_column("Station", justify="left")
    table.add_column("URL / UUID", justify="left")

    if len(alias.alias_map) > 0:
        for entry in alias.alias_map:
            table.add_row(entry["name"], entry["uuid_or_url"])
        _console.print(table)
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
        width=80,
        safe_box=False,
        expand=False,
    )
    table.add_column("Station", justify="left")
    table.add_column("URL / UUID", justify="left")

    if len(history.history_list) > 0:
        for entry in history.history_list:
            table.add_row(entry["name"], entry["uuid_or_url"])
        _console.print(table)
        log.info(f"Your history is saved in {history.history_path}")
    else:
        log.info("You have no history")


def handle_show_station_info() -> None:
    """Show important information regarding the current station."""
    custom_info = []
    try:
        # Create a clean table for station info instead of a dict dump
        table = Table(box=None, padding=(0, 2))
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Name", global_current_station_info.get("name"))
        table.add_row("URL", global_current_station_info.get("url"))
        table.add_row("Website", global_current_station_info.get("homepage"))
        table.add_row("Country", global_current_station_info.get("country"))
        table.add_row("Language", global_current_station_info.get("language"))
        table.add_row("Codec", global_current_station_info.get("codec"))
        table.add_row("Bitrate", str(global_current_station_info.get("bitrate", "N/A")))

        info_panel = Panel(table, title="[b]Station Info[/b]", width=80, expand=False)
        _console.print(info_panel)
    except Exception as e:
        log.error(f"No station information available: {e}")


def handle_current_play_panel(curr_station_name: str = "") -> None:
    """
    Update the current station banner and manage the Live display lifecycle.
    """
    global _live_display, _station_banner
    _station_banner = _get_banner_panel(curr_station_name)

    if _live_display is None:
        _live_display = Live(
            _get_composite_renderable(),
            console=_console,
            auto_refresh=False,
            transient=False,
        )
        _live_display.start()
    else:
        refresh_live_display()


def stop_live_display() -> None:
    """Stop the global live display."""
    global _live_display, _prompt_renderable
    if _live_display:
        try:
            _live_display.stop()
        except Exception:
            pass
        _live_display = None
    _prompt_renderable = None


def set_live_display(live: Optional[Live]) -> None:
    """Set the active live display instance."""
    global _live_display
    _live_display = live


def get_live_display() -> Optional[Live]:
    """Return the active live display instance."""
    return _live_display


def get_current_banner() -> Optional[Group]:
    """
    Return app + station banners as one Group for standalone display (e.g. fallback Live).
    None if neither banner is set.
    """
    parts = [c for c in [_app_banner, _station_banner] if c is not None]
    if not parts:
        return None
    return Group(*parts)


def update_prompt_renderable(renderable: Optional[Any] = None):
    """Update the prompt portion of the persistent UI."""
    global _prompt_renderable
    _prompt_renderable = renderable
    refresh_live_display()


def handle_input(prompt: str) -> str:
    """
    Standard input wrapper. Uses the active live display's console if available
    to prevent UI corruption.
    """
    try:
        if _live_display:
            # use the live console to print above the banner
            res = _live_display.console.input(prompt)
        else:
            res = input(prompt)
        return res
    except EOFError:
        return ""
    except Exception as e:
        log.debug(f"Input error: {e}")
        return ""


def set_global_station_info(info: dict) -> None:
    """Helper to update global station info from other modules."""
    global global_current_station_info
    global_current_station_info = info


def get_global_station_info() -> dict:
    """Helper to get global station info."""
    return global_current_station_info
