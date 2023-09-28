from rich.console import Console
from rich.panel import Panel
from rich.table import Table


def show_help():
    """Show help message as table"""
    console = Console()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Arguments", justify="left")
    table.add_column("Description", justify="left")
    table.add_column("Default", justify="center")

    table.add_row(
        "--search , -S",
        "A station name to search on the internet",
        "",
    )
    table.add_row(
        "--play , -P",
        "A station name from fav list or a stream url",
        "",
    )
    table.add_row(
        "--last",
        "Play last played station",
        "False",
    )
    table.add_row(
        "--uuid , -U",
        "A station UUID to play it directly",
        "",
    )
    table.add_row(
        "--loglevel",
        "Log level of the program: info,warning,error,debug",
        "info",
    )
    table.add_row(
        "--add-station , -A",
        "Add a station to your favorite list",
        "False",
    )
    table.add_row(
        "--add-to-favorite, -F ",
        "Add current station to favorite list",
        "False",
    )

    table.add_row(
        "--show-favorite-list, -W ",
        "Show your favorite list",
        "False",
    )

    table.add_row(
        "--discover-by-country, -D",
        "Discover stations by country code",
        "False",
    )

    table.add_row(
        "--discover-by-state",
        "Discover stations by country state",
        "False",
    )

    table.add_row(
        "--discover-by-tag",
        "Discover stations by tags/genre",
        "False",
    )

    table.add_row(
        "--discover-by-language",
        "Discover stations by language",
        "False",
    )

    table.add_row(
        "--limit, -L",
        "Limit the number of station results",
        "100",
    )

    table.add_row(
        "--volume, -V",
        "Volume of the radio between 0 and 100",
        "80",
    )

    table.add_row(
        "--flush",
        "Clear your favorite list",
        "False",
    )
    table.add_row(
        "--record, -R",
        "Record current stations audio",
        "False",
    )

    table.add_row(
        "--filepath",
        "Path to save the recorded audio",
        "<User/Music/radioactive>",
    )

    table.add_row(
        "--filename, -N",
        "Filename to save the recorded audio",
        "<station-timestamp>",
    )
    table.add_row(
        "--filetype, -T",
        "Type / format of target recording",
        "mp3",
    )

    table.add_row(
        "--kill, -K",
        "Stop background radios",
        "False",
    )

    console.print(table)
