from zenlog import log
from rich.panel import Panel
from rich.console import Console
from rich.table import Table


def show_help():
    """ Show help message as table """
    console = Console()

    welcome = Panel(
    """
        :radio: Play any radios around the globe right from this Terminal [yellow][blink]:zap:[/blink][/yellow]!
        :smile: Author: Dipankar Pal
        :question: Type '--help' for more details on avaliable commands.
        :bug: Visit https://github.com/deep5050/radio-active to submit issues
        :star: Show some love by starring the project on GitHub [red][blink]:heart:[/blink][/red]
        """,
    title="[rgb(250,0,0)]RADIO[rgb(0,255,0)]ACTIVE",
    width=85
    )
    console.print(welcome)

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Arguments", justify="center")
    table.add_column("Expects value", justify="center")
    table.add_column("Description", justify="center")
    table.add_column("Default", justify="center")
    table.add_column("Note", justify="center")

    table.add_row("--station , -S","yes","A station name to play","","Optional from second run")
    table.add_row("--uuid , -U","yes","A station UUID to play","","Optional from second run")
    table.add_row("--log-level , -L","yes [info,warning,error,debug]","Log level of the program","info","Optional")
    table.add_row("--add-station , -A","no","Add a  station to your favourite list","False","Optional")
    table.add_row("--add-to-favourite, -F ","yes","Add current station to favourite list with custom name","False","Optional")
    table.add_row("--show-favourite-list, -W ","no","Show your favourite list","False","Optional")
    table.add_row("--flush,","no","Clear your favourite list","False","Optional")


    console.print(table)