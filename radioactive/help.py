from rich.console import Console
from rich.panel import Panel
from rich.table import Table


def show_help():
    """Show help message as table"""
    console = Console()

    welcome = Panel(
        """
        :radio: Play any radios around the globe right from this Terminal [yellow][blink]:zap:[/blink][/yellow]!
        :smile: Author: Dipankar Pal
        :question: Type '--help' for more details on available commands.
        :bug: Visit https://github.com/deep5050/radio-active to submit issues
        :star: Show some love by starring the project on GitHub [red][blink]:heart:[/blink][/red]
        :dollar: You can donate me at https://deep5050.github.io/payme/
        """,
        title="[b]RADIOACTIVE[/b]",
        width=85,
    )
    console.print(welcome)

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Arguments", justify="left")
    table.add_column("Expects value", justify="center")
    table.add_column("Description", justify="left")
    table.add_column("Default", justify="center")
    table.add_column("Note", justify="center")

    table.add_row(
        "--station , -S",
        "yes",
        "A station name to search on the internet",
        "",
        "Optional from second run",
    )
    table.add_row(
        "--uuid , -U",
        "yes",
        "A station UUID to play it directly",
        "",
        "Optional from second run",
    )
    table.add_row(
        "--log-level , -L",
        "yes [info,warning,error,debug]",
        "Log level of the program",
        "info",
        "Optional",
    )
    table.add_row(
        "--add-station , -A",
        "no",
        "Add a  station to your favorite list",
        "False",
        "Optional",
    )
    table.add_row(
        "--add-to-favorite, -F ",
        "yes",
        "Add current station to favorite list with custom name",
        "False",
        "Optional",
    )

    table.add_row(
        "--show-favorite-list, -W ",
        "no",
        "Show your favorite list",
        "False",
        "Optional",
    )

    table.add_row(
        "--discover-by-country, -D",
        "yes",
        "Discover stations by country code",
        "False",
        "Optional",
    )

    table.add_row(
        "--discover-by-state",
        "yes",
        "Discover stations by country state",
        "False",
        "Optional",
    )

    table.add_row(
        "--discover-by-tag",
        "yes",
        "Discover stations by tags/genre",
        "False",
        "Optional",
    )

    table.add_row(
        "--discover-by-language",
        "yes",
        "Discover stations by language",
        "False",
        "Optional",
    )

    table.add_row(
        "--limit",
        "yes",
        "Limit the number of results in discover result table",
        "100",
        "Optional",
    )

    table.add_row(
        "--volume",
        "yes",
        "Volume of the radio between 0 and 100",
        "80",
        "Optional",
    )

    table.add_row("--flush", "no", "Clear your favorite list", "False", "Optional")
    table.add_row("--kill", "no", "Stop background radios", "False", "Optional")

    console.print(table)
