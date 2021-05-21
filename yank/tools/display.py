# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ RICH IMPORTS                                                                       │
# └────────────────────────────────────────────────────────────────────────────────────┘

from rich.padding import Padding
from rich.table import Table


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ GET COMMANDS RENDERABLE                                                            │
# └────────────────────────────────────────────────────────────────────────────────────┘


def get_commands_renderable(title, *commands):
    """ Returns a Rich Table containing available commands """

    # Initialize Rich Table as renderable
    renderable = Table(title=title)

    # Add columns
    [
        renderable.add_column(col_name)
        for col_name in (
            "#",
            "command",
            "arguments",
            "description",
            "example",
        )
    ]

    # Add quit command to end of commands
    commands = commands + (("q[uit]", "", "Quit or go back", "q"),)

    # Iterate over commands
    for i, (command, arguments, description, example) in enumerate(commands):

        # Add square bracket escape in command
        command = command.replace("[", "\[")  # noqa

        # Add row
        renderable.add_row(str(i), command, arguments or "", description, example or "")

    # Pad the renderable
    renderable = Padding(renderable, (1, 1))

    # Return renderable
    return renderable


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ DISPLAY COMMANDS                                                                   │
# └────────────────────────────────────────────────────────────────────────────────────┘


def display_commands(title, console, *commands):
    """ Displays a commands renderable in a pager """

    # Initialize pager
    with console.pager():

        # Get commands renderable
        commands_renderable = get_commands_renderable(title, *commands)

        # Display commands
        console.print(commands_renderable, justify="center")
