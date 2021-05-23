# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ GENERAL IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import re

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ RICH IMPORTS                                                                       │
# └────────────────────────────────────────────────────────────────────────────────────┘

from rich.console import Console
from rich.padding import Padding
from rich.table import Table

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ PROJECT IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import yank.constants as _c

from yank.tools import display_commands


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ YANKER DISPLAY MIXIN                                                               │
# └────────────────────────────────────────────────────────────────────────────────────┘


class YankerDisplayMixin:
    """ Yanker Display Mixin """

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CLASS ATTRIBUTES                                                               │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # Initialize cached console to None
    _console = None

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ TABLE NAMES                                                                    │
    # └────────────────────────────────────────────────────────────────────────────────┘

    @property
    def table_names(self):
        """ Returns a list of table names in the database """

        # Return table names
        return list(self.tables.keys())

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CONSOLE                                                                        │
    # └────────────────────────────────────────────────────────────────────────────────┘

    @property
    def console(self):
        """ Returns a cached or newly initialized Rich console object """

        # Check if console is cached
        if self._console:

            # Return cached console
            return self._console

        # Initialize a new Rich console
        console = Console()

        # Cache console
        self._console = console

        # Return console
        return console

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ DISPLAY TABLES                                                                 │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def display_tables(self, interactive=False):
        """ Displays a list of tables using a Rich Table """

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ STATIC                                                                     │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Get tables
        tables = [(name, interface) for name, interface in self.tables.items()]

        # Get console
        console = self.console

        # Clear console if interactive
        interactive and console.clear()

        # Get renderable
        renderable = self.get_tables_renderable(tables=tables, interactive=interactive)

        # Print renderable
        console.print(renderable, justify="center")

        # Return if not interactive
        if not interactive:
            return

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ INTERACTIVE                                                                │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Initialize while loop
        while True:

            # Get command
            command = console.input(_c.INPUT_TAG)

            # Handle case of quit
            if command in ["q", "quit"]:
                break

            # Otherwise handle case of command
            elif command in ["c", "command", "commands"]:

                # Display commands
                display_commands(
                    "Available Commands",
                    console,
                    ("r[ows]", "<#>", "Show table rows", "r 0"),
                    ("c[ols]", "<#>", "Show table columns", "c 0"),
                )

            # Get command and index
            match = re.search(r"(\w+) *(\d+)", command)

            # Check if match is not null
            if match:

                # Separate index from command
                command, idx = (match.group(1).lower().strip(), int(match.group(2)))

                # Initialize try-except block
                try:

                    # Get table name and interface
                    table_name, interface = tables[idx]

                # Handle IndexError
                except IndexError:

                    # Set table name and interface to None
                    table_name = interface = None

                # Check if table name and interface are not null
                if table_name and interface:

                    # Handle case of columns
                    if command in ["c", "cols", "columns"]:

                        # Display table
                        self.display_table(table_name, interactive=interactive)

                    # Otherwise handle case of rows
                    elif command in ["r", "rows"]:

                        # Display interface list view
                        interface.display_list(interactive=interactive)

            # Clear console
            console.clear()

            # Print renderable
            console.print(renderable, justify="center")

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ GET TABLES RENDERABLE                                                          │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def get_tables_renderable(self, tables, interactive=False):
        """ Displays a list of tables using a Rich Table """

        # Get table count
        table_count = len(tables)

        # Initialize Rich Table as renderable
        renderable = Table(
            title=(
                f"Tables: {self.db_name} "
                f"({table_count} {self.inflector.plural('table', table_count)})"
            )
        )

        # Check if interactive
        if interactive:

            # Set caption
            renderable.caption = "c\[ommands]: Show available commands"  # noqa

        # Add columns
        [
            renderable.add_column(col_name)
            for col_name in ("#", "name", "interface", "cols", "rows")
        ]

        # Iterate over tables
        for i, (table_name, interface) in enumerate(tables):

            # Get column count
            col_count = str(len(interface.Item.__table__.columns))

            # Get row count
            row_count = str(interface.count())

            # Add row
            renderable.add_row(
                str(i), interface.db_table_name, interface.name, col_count, row_count
            )

        # Pad the renderable
        renderable = Padding(renderable, (1, 1))

        # Return renderable
        return renderable

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ DISPLAY TABLE                                                                  │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def display_table(self, name, interactive=False):
        """ Displays a list of columns of a table using a Rich Table """

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ STATIC                                                                     │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Get table renderable
        renderable = self.get_table_renderable(name, interactive=interactive)

        # Get console
        console = self.console

        # Clear console if interactive
        interactive and console.clear()

        # Print renderable
        console.print(renderable, justify="center")

        # Return if not interactive
        if not interactive:
            return

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ INTERACTIVE                                                                │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Initialize while loop
        while True:

            # Get command
            command = console.input(_c.INPUT_TAG)

            # Handle case of quit
            if command in ["q", "quit"]:
                break

            # Otherwise handle case of command
            elif command in ["c", "command", "commands"]:

                # Display commands
                display_commands(title="Available Commands", console=console)

            # Clear console
            console.clear()

            # Print renderable
            console.print(renderable, justify="center")

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ GET TABLE RENDERABLE                                                           │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def get_table_renderable(self, name, interactive=False):
        """ Returns a Rich table renderable """

        # Get interface
        interface = self.tables.get(name)

        # Return if interface is null
        if not interface:
            return

        # Get field map
        field_map = interface.field_map

        # Get column count
        col_count = len(field_map)

        # Initialize Rich Table as renderable
        renderable = Table(
            title=f"Table: {name} ({col_count} "
            f"{self.inflector.plural('col', col_count)})"
        )

        # Check if interactive
        if interactive:

            # Set caption
            renderable.caption = "c\[ommands]: Show available commands"  # noqa

        # Add columns
        [
            renderable.add_column(col_name)
            for col_name in ("#", "field", "display", "cast", "type")
        ]

        # Iterate over field map
        for i, (field, info) in enumerate(field_map.items()):

            # Get cast
            cast = info[_c.CAST]

            # Add row
            renderable.add_row(
                str(i),
                field,
                info[interface.DISPLAY],
                str(cast),
                str(interface.TYPE_MAP[cast]),
            )

        # Pad the renderable
        renderable = Padding(renderable, (1, 1))

        # Return renderable
        return renderable
