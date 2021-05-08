# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ GENERAL IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import math
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


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ INTERFACE DISPLAY MIXIN                                                            │
# └────────────────────────────────────────────────────────────────────────────────────┘


class InterfaceDisplayMixin:
    """ Interface Display Mixin """

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CLASS ATTRIBUTES                                                               │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # Initialize cached console to None
    _console = None

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
    # │ GET LIST RENDERABLE                                                            │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def get_list_renderable(self, interactive=False, limit=None, offset=0):
        """ Returns a Rich table renderable for the interface list view """

        # Get row count
        row_count = self.count()

        # Initialize Rich Table as renderable
        renderable = Table(
            title=f"{self.name}: {self.db_table_name} ({row_count} rows)"
        )

        # Check if interactive
        if interactive:

            # Check if limit is defined
            if limit:

                # Get page count
                page_count = math.ceil(row_count / limit)

                # Add page number to title
                renderable.title += f"\nPage {int(offset / limit) + 1} of {page_count}"

            # Set caption
            renderable.caption = "c\[ommands]: Display available commands"  # noqa

        # Get display fields
        display_fields = self.display_list_by

        # Check if display fields is None
        if not display_fields:

            # Define display list by as the first n fields in the field map
            display_fields = list(self.field_map.keys())[:5]

        # Add ID to display fields
        display_fields = ["id"] + list(display_fields)

        # Initialize fields
        fields = []

        # Iterate over display fields
        for display_field in display_fields:

            # Get field and display
            field, display = (
                display_field
                if type(display_field) in [list, tuple]
                else (display_field, display_field.replace("_", " "))
            )

            # Create column
            renderable.add_column(display)

            # Add field to fields
            fields.append(field)

        # Get items
        items = self.db_session.query(self.Item)

        # Check if limit is not null
        if limit:

            # Limit items
            items = items.offset(offset).limit(limit)

        # Apply filter to items
        items = items.all()

        # Iterate over items
        for item in items:

            # Add row
            renderable.add_row(*[str(getattr(item, field)) for field in fields])

        # Pad renderable
        renderable = Padding(renderable, (1, 1))

        # Return renderable and row count
        return renderable, row_count

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ GET LIST COMMANDS RENDERABLE                                                   │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def get_list_commands_renderable(self):
        """ Returns a Rich table renderable for commands of the interface list view """

        # Initialize Rich Table as renderable
        renderable = Table(title="List View Commands")

        # Add columns
        [
            renderable.add_column(col_name)
            for col_name in ("#", "command", "argument", "description", "example")
        ]

        # Define commands
        commands = (
            ("'", "[<int>]", "Go to next \[nth] page", "' 5"),  # noqa
            (";", "[<int>]", "Go to previous \[nth] page", "; 3"),  # noqa
            ("l\[imit]", "<int>", "Set max number of rows per page", "l 10"),  # noqa
            (
                "s\[ort]",
                "<field>[,<field>]",
                "Sort rows by field(s)",
                "s name,-age",
            ),  # noqa
            (
                "f\[ilter]",
                "<field>=<value>[,<field>=<value>]",
                "Filter rows by field(s)",
                "f name=Bob,age=24",
            ),  # noqa
            ("d\[etail]", "<id>", "Display a row in detail view", "d 5"),  # noqa
            ("r\[eset]", None, "Reset sort and filter parameters", "r"),  # noqa
        )

        # Iterate over commands
        for i, (command, arguments, description, example) in enumerate(commands):

            # Add row
            renderable.add_row(
                str(i), command, arguments or "", description, example or ""
            )

        # Pad the renderable
        renderable = Padding(renderable, (1, 1))

        # Return renderable
        return renderable

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ DISPLAY LIST                                                                   │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def display_list(self, interactive=False, limit=20, offset=0, return_callback=None):
        """ Displays a list of items using a Rich Table """

        # Get console
        console = self.console

        # Check if not interactive
        if not interactive:

            # Get list renderable
            renderable = self.get_list_renderable()

            # Print renderable list view and return
            console.print(renderable, justify="center")
            return

        # Get renderable
        renderable, row_count = self.get_list_renderable(
            interactive=interactive, limit=limit, offset=offset
        )

        # Clear console
        console.clear()

        # Print renderable list view and return
        console.print(renderable, justify="center")

        # Initialize while loop
        while True:

            # Get command
            command = console.input(_c.INPUT_TAG)

            # Otherwise handle case of reset
            if command in ["r", "reset"]:
                pass

            # Otherwise handle case of quit
            elif command in ["q", "quit"]:
                break

            # Otherwise handle case of command
            elif command in ["c", "command", "commands"]:

                # Initialize pager
                with console.pager():

                    # Get table renderable
                    renderable = self.get_list_commands_renderable()

                    # Print table renderable
                    console.print(renderable, justify="center")

            # Otherwise handle more complex commands
            else:

                # Get command and index
                match = re.search(r"([a-zA-Z';]+) *(.*)", command)

                # Continue if match is null
                if not match:
                    continue

                # Separate args from command
                command, args = match.group(1).strip(), match.group(2)

                # Handle case of next page
                if command == "'":

                    # Define multiplier
                    multiplier = int(args) if args.isdigit() else 1

                    # Get new offset
                    new_offset = offset + (limit * multiplier)

                    # Increment offset by limit
                    offset = offset if new_offset >= row_count else new_offset

                # Otherwise handle case of previous page
                elif command == ";":

                    # Get new offset
                    new_offset = offset - (limit * multiplier)

                    # Decrement offset by limit
                    offset = max(new_offset, 0)

                # Otherwise handle case of limit
                elif command in ["l", "limit"]:

                    # Set new limit
                    limit = max(int(args), 0) if args.isdigit() else None

                    # Reset offset to 0
                    offset = 0

            # Get renderable and row count
            renderable, row_count = self.get_list_renderable(
                interactive=interactive, limit=limit, offset=offset
            )

            # Clear console
            console.clear()

            # Print renderable list view and return
            console.print(renderable, justify="center")

        # Check if return callback is not null
        if return_callback:

            # Call return callback
            return_callback()
