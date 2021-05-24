# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ RICH IMPORTS                                                                       │
# └────────────────────────────────────────────────────────────────────────────────────┘

from rich.padding import Padding
from rich.table import Table


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ GET TABLE RENDERABLE                                                               │
# └────────────────────────────────────────────────────────────────────────────────────┘


def get_table_renderable(title, cols, rows):
    """ Returns a Rich Table constructed from supplied cols and rows """

    # Initialize Rich Table as renderable
    renderable = Table(title=title)

    # Add number column
    renderable.add_column("#")

    # Add columns
    [renderable.add_column(col) for col in cols]

    # Iterate over rows
    for i, row in enumerate(rows):

        # Add row
        renderable.add_row(str(i), *[str(r) if r else "" for r in row])

    # Pad the renderable
    renderable = Padding(renderable, (1, 1))

    # Return renderable
    return renderable


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ GET COMMANDS RENDERABLE                                                            │
# └────────────────────────────────────────────────────────────────────────────────────┘


def get_commands_renderable(title, *commands):
    """ Returns a Rich Table containing available commands """

    # Initialize Rich Table as renderable
    renderable = Table(title=title)

    # Define columns
    cols = (
        "command",
        "arguments",
        "description",
        "example",
    )

    # Convert commands to list
    commands = [list(c) for c in commands]

    # Add quit command to end of commands
    commands = commands + [["q[uit]", "", "Quit or go back", "q"]]

    # Iterate over commands
    for i, command in enumerate(commands):

        # Get command
        command = command[0]

        # Add square bracket escape in command
        command = command.replace("[", "\[")  # noqa

        # Replace command
        commands[i][0] = command

    # Get commands renderable
    renderable = get_table_renderable(title, cols, commands)

    # Return renderable
    return renderable


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ DISPLAY COMMANDS                                                                   │
# └────────────────────────────────────────────────────────────────────────────────────┘


def display_commands(title, console, *commands, aux_tables=None):
    """ Displays a commands renderable in a pager """

    # Initialize pager
    with console.pager():

        # Get commands renderable
        commands_renderable = get_commands_renderable(title, *commands)

        # Display commands
        console.print(commands_renderable, justify="center")

        # Check if aux tables is not null
        if aux_tables:

            # Iterate over aux tables
            for title, cols, rows in aux_tables:

                # Get renderable
                renderable = get_table_renderable(title, cols, rows)

                # Display aux table
                console.print(renderable, justify="center")
