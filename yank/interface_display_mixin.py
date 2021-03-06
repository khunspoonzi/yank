# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ GENERAL IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import math
import re

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ RICH IMPORTS                                                                       │
# └────────────────────────────────────────────────────────────────────────────────────┘

from rich.columns import Columns
from rich.console import Console, RenderGroup
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ PROJECT IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import yank.constants as _c

from yank.tools import display_commands

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ CONSTANTS                                                                          │
# └────────────────────────────────────────────────────────────────────────────────────┘

# Define AND operator
OPERATOR_AND = "&&"

# Define OR operator
OPERATOR_OR = "||"


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

    def get_list_renderable(
        self,
        interactive=False,
        limit=None,
        offset=0,
        sort_by=None,
        filter_by=None,
        highlight_id=None,
    ):
        """ Returns a Rich table renderable for the interface list view """

        # Define max limit
        limit_max = 1000

        # Initialize limie
        limit = limit or limit_max

        # Get limit where max is 1000
        limit = min(limit, limit_max)

        # Get display map
        display_map = self.list_display_map

        # Get items
        items = self.db_session.query(self.Item)

        # Check if filter by is not null
        if filter_by:

            # Apply filters
            items = self.filter(
                queryset=items, display_map=display_map, tuples=filter_by
            )

        # Check if sort by is not null
        if sort_by:

            # Apply sort fields
            items = self.sort(*sort_by, queryset=items, display_map=display_map)

        # Get row count
        row_count = items.count()

        # Get page count
        page_count = math.ceil(row_count / limit)

        # Define title
        title = (
            f"{self.name}: {self.db_table_name}\n"
            f"Page {int(offset / limit) + 1} of {page_count} "
            f"({row_count} {self.inflector.plural('row', row_count)})"
        )

        # Limit items
        items = items.offset(offset).limit(limit)

        # Initialize Rich Table as renderable
        renderable = Table(title=title)

        # Get display fields
        display_fields = self.display_list_by

        # Initialize fields
        fields = []

        # Iterate over display fields
        for field, display in display_fields.items():

            # Create column
            renderable.add_column(display)

            # Add field to fields
            fields.append(field)

        # Iterate over items
        for item in items:

            # Initialize style
            style = ""

            # Get item ID
            item_id = item.id

            # Check if item is highlighted
            if item_id == highlight_id:

                # Set style
                style = "white on blue"

            # Add row
            renderable.add_row(
                *[str(getattr(item, field)) for field in fields], style=style
            )

        # Check if interactive
        if interactive:

            # Initialize caption
            caption = "c\[ommands]: Show available commands"  # noqa

            # Initialize sub-caption
            sub_caption = ""

            # Check if sort by is not null
            if sort_by:

                # Add sort sub-caption
                sub_caption += f"sort {(' ' + OPERATOR_AND + ' ').join(sort_by)}\n"

            # Check if filter by is not null
            if filter_by:

                # Get filter strings
                filter_strings = [f"{f} = {v}" for f, v in filter_by]

                # Add filter sub-caption
                sub_caption += (
                    f"filter {(' ' + OPERATOR_AND + ' ').join(filter_strings)}\n"
                )

            # Check if sub-caption
            if sub_caption:

                # Combine caption and sub-caption
                caption = sub_caption + "\n" + caption

            # Set caption
            renderable.caption = caption.strip("\n")

        # Pad renderable
        renderable = Padding(renderable, (1, 1))

        # Return renderable and row count
        return renderable, row_count

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ DISPLAY LIST                                                                   │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def display_list(
        self,
        interactive=False,
        limit=20,
        offset=0,
        sort_by=None,
        filter_by=None,
    ):
        """ Displays a list of items using a Rich Table """

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ STATIC                                                                     │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Get renderable
        renderable, row_count = self.get_list_renderable(
            interactive=interactive,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            filter_by=filter_by,
        )

        # Get console
        console = self.console

        # Clear console
        console.clear()

        # Print renderable list view and return
        console.print(renderable, justify="center")

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ INTERACTIVE                                                                │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Return if not interactive
        if not interactive:
            return

        # Initialize highlight ID
        highlight_id = None

        # Define sort commands
        sort_commands = ("s", "sort")

        # Define filter commands
        filter_commands = ("f", "filter")

        # Define reset commands
        reset_commands = ("r", "reset")

        # Cache previous item URL
        item_url_previous = None

        # Initialize while loop
        while True:

            # Get command
            command = console.input(_c.INPUT_TAG)

            # ┌────────────────────────────────────────────────────────────────────────┐
            # │ BASIC COMMANDS                                                         │
            # └────────────────────────────────────────────────────────────────────────┘

            # Otherwise handle case of reset
            if command in reset_commands:

                # Reset sort fields
                sort_by = None

                # Reset filters
                filter_by = None

            # Otherwise handle case of quit
            elif command in ["q", "quit"]:
                break

            # Otherwise handle case of command
            elif command in ["c", "command", "commands"]:

                # Display commands
                display_commands(
                    "List View Commands",
                    console,
                    ("'", "<int> = 1", "Go to next nth page", "' 5"),
                    (";", "<int> = 1", "Go to previous nth page", "; 3"),
                    ("l[imit]", "<int>", "Set max number of rows per page", "l 10"),
                    (
                        "s[ort]",
                        f"<field>[ {OPERATOR_AND} <field>]",
                        "Sort rows by field(s)",
                        "s name && -age",
                    ),
                    (
                        "f[ilter]",
                        f"<field> = <value>[ {OPERATOR_AND} <field> = <value>]",
                        "Filter rows by field(s)",
                        "f name = Bob && age = 24",
                    ),
                    (
                        "r[eset]",
                        f"<command>[ {OPERATOR_AND} <command>] = sort && filter",
                        "Reset sort and / or filter parameters",
                        "r sort",
                    ),
                    ("d[etail]", "<id>", "Display a row in detail view", "d 5"),
                    ("o[pen]", "<id>", "Opens a row's URL in a browser", "o 5"),
                    aux_tables=[
                        (
                            "Filter Modifiers",
                            (
                                "modifier",
                                "usage",
                                "filters rows based on the...",
                                "example",
                            ),
                            (
                                (
                                    "exact",
                                    "<field> = <value>",
                                    "exact value of a field",
                                    "f name = Bob",
                                ),
                                (
                                    "iexact",
                                    "<field>__iexact = <value>",
                                    (
                                        "exact "
                                        "case-insensitive value of a string-based field"
                                    ),
                                    "f name = bob",
                                ),
                                (
                                    "contains",
                                    "<field>__contains = <substring>",
                                    (
                                        "presence of a "
                                        "substring in a string-based field"
                                    ),
                                    "f name__contains = Bo",
                                ),
                                (
                                    "icontains",
                                    "<field>__icontains = <substring>",
                                    (
                                        "presence of a "
                                        "case-insensitive substring in a string-based "
                                        "field"
                                    ),
                                    "f name__icontains = bo",
                                ),
                                (
                                    "startswith",
                                    "<field>__startswith = <substring>",
                                    (
                                        "presence of a "
                                        "substring at the start of a string-based "
                                        "field"
                                    ),
                                    "f name__startswith = Bo",
                                ),
                                (
                                    "istartswith",
                                    "<field>__istartswith = <substring>",
                                    (
                                        "presence of a "
                                        "case-insensitive substring at the start "
                                        "of a string-based field"
                                    ),
                                    "f name__istartswith = bo",
                                ),
                                (
                                    "endswith",
                                    "<field>__endswith = <substring>",
                                    (
                                        "presence of a "
                                        "substring at the end of a string-based "
                                        "field"
                                    ),
                                    "f name__endswith = ob",
                                ),
                                (
                                    "iendswith",
                                    "<field>__iendswith = <substring>",
                                    (
                                        "presence of a "
                                        "case-insensitive substring at the end "
                                        "of a string-based field"
                                    ),
                                    "f name__iendswith = OB",
                                ),
                                (
                                    "regex",
                                    "<field>__regex = <pattern>",
                                    (
                                        "positive match of a "
                                        "regex pattern against the value of a "
                                        "string-based field"
                                    ),
                                    "f name__regex = ^[A-Z]\[a-z]{2}$",  # noqa
                                ),
                                (
                                    "in",
                                    "<field>__in = <value>, <value>",
                                    (
                                        "exact value of any one of the "
                                        "options in a comma-separated list "
                                    ),
                                    "f name__in = Bob, Tom",
                                ),
                                (
                                    "iin",
                                    "<field>__iin = <value>, <value>",
                                    (
                                        "exact case-insensitive value of a "
                                        "string-based field against any one of the "
                                        "options in a comma-separated list "
                                    ),
                                    "f name__iin = bob, tom",
                                ),
                            ),
                        ),
                        (
                            "Filter Operators",
                            (
                                "operator",
                                "usage",
                                "description",
                                "example",
                            ),
                            (
                                (
                                    "~",
                                    "~ <field>[__modifier] = <value>",
                                    (
                                        "Negates the filter to exclude the selected "
                                        "rows"
                                    ),
                                    "f ~ name = Bob",
                                ),
                                (
                                    "&&",
                                    (
                                        "<field>[__modifier] = <value> && "
                                        "<field>[__modifier] = <value>"
                                    ),
                                    (
                                        "Selects rows that satisfy all of the chained "
                                        "filters"
                                    ),
                                    "f name = Bob && age = 24",
                                ),
                            ),
                        ),
                    ],
                )

            # ┌────────────────────────────────────────────────────────────────────────┐
            # │ ARGUMENT COMMANDS                                                      │
            # └────────────────────────────────────────────────────────────────────────┘

            # Otherwise handle more complex commands
            else:

                # Get command and index
                match = re.search(r"([a-zA-Z';]+) *(.*)", command)

                # Separate args from command
                command, args = (
                    (match.group(1).strip(), match.group(2)) if match else (None, None)
                )

                # ┌────────────────────────────────────────────────────────────────────┐
                # │ NEXT PAGE                                                          │
                # └────────────────────────────────────────────────────────────────────┘

                # Handle case of next page
                if command == "'":

                    # Define multiplier
                    multiplier = int(args) if args.isdigit() else 1

                    # Get new offset
                    new_offset = offset + (limit * multiplier)

                    # Increment offset by limit
                    offset = offset if new_offset >= row_count else new_offset

                # ┌────────────────────────────────────────────────────────────────────┐
                # │ PREVIOUS PAGE                                                      │
                # └────────────────────────────────────────────────────────────────────┘

                # Otherwise handle case of previous page
                elif command == ";":

                    # Define multiplier
                    multiplier = int(args) if args.isdigit() else 1

                    # Get new offset
                    new_offset = offset - (limit * multiplier)

                    # Decrement offset by limit
                    offset = max(new_offset, 0)

                # ┌────────────────────────────────────────────────────────────────────┐
                # │ LIMIT                                                              │
                # └────────────────────────────────────────────────────────────────────┘

                # Otherwise handle case of limit
                elif command in ["l", "limit"]:

                    # Set new limit
                    limit = max(int(args), 0) if args.isdigit() else None

                    # Reset offset to 0
                    offset = 0

                # ┌────────────────────────────────────────────────────────────────────┐
                # │ SORT                                                               │
                # └────────────────────────────────────────────────────────────────────┘

                # Otherwise handle case of sort
                elif command in sort_commands:

                    # Set sort by argument
                    sort_by = [f.strip() for f in args.split(OPERATOR_AND)]

                    # Remove null items
                    sort_by = [s for s in sort_by if s]

                    # Set to None if null
                    sort_by = sort_by or None

                    # Reset offset to zero
                    offset = 0

                # ┌────────────────────────────────────────────────────────────────────┐
                # │ FILTER                                                             │
                # └────────────────────────────────────────────────────────────────────┘

                # Otherwise handle case of filter
                elif command in filter_commands:

                    # Set filter by argument
                    filter_by = [f.strip() for f in args.split(OPERATOR_AND)]

                    # Convert filter by to list of tuples
                    filter_by = (
                        [[f.strip() for f in arg.split("=")] for arg in filter_by]
                        if filter_by
                        else None
                    )

                    # Reset offset to zero
                    offset = 0

                # ┌────────────────────────────────────────────────────────────────────┐
                # │ RESET                                                              │
                # └────────────────────────────────────────────────────────────────────┘

                # Otherwise handle case of reset
                elif command in reset_commands:

                    # Iterate over split args
                    for arg in (args or "").split(OPERATOR_AND):

                        # Strip arg
                        arg = arg.strip()

                        # Handle case of sort
                        if arg in sort_commands:

                            # Set sort by to None
                            sort_by = None

                        # Otherwise handle case of filter
                        elif arg in filter_commands:

                            # Set filter by to None
                            filter_by = None

                # ┌────────────────────────────────────────────────────────────────────┐
                # │ DETAIL                                                             │
                # └────────────────────────────────────────────────────────────────────┘

                # Otherwise handle case of detail
                elif command in ["d", "detail"]:

                    # Get item ID
                    item_id = int(args)

                    # Display interface detail view
                    self.display_detail(item_id=item_id, interactive=interactive)

                # ┌────────────────────────────────────────────────────────────────────┐
                # │ OPEN                                                               │
                # └────────────────────────────────────────────────────────────────────┘

                # Otherwise handle case of open
                elif command in ["o", "open"]:

                    # Get item ID
                    item_id = int(args)

                    # Set highlight ID
                    highlight_id = item_id

                    # Get item
                    item = self.get(id=item_id)

                    # Get item URL
                    item_url = item.url

                    # Check if item URL does not equal previous item URL
                    if item_url != item_url_previous:

                        # Get item URL with driver
                        self.browser.driver.get(item_url)

                    # Cache previous item URL
                    item_url_previous = item_url

            # ┌────────────────────────────────────────────────────────────────────────┐
            # │ RE-RENDER                                                              │
            # └────────────────────────────────────────────────────────────────────────┘

            # Get renderable and row count
            renderable, row_count = self.get_list_renderable(
                interactive=interactive,
                limit=limit,
                offset=offset,
                sort_by=sort_by,
                filter_by=filter_by,
                highlight_id=highlight_id,
            )

            # Clear console
            console.clear()

            # Print renderable list view and return
            console.print(renderable, justify="center")

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ GET DETAIL RENDERABLE                                                          │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def get_detail_renderable(self, item_id):

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ GET ITEM                                                                   │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Get item by ID
        item = self.get(id=int(item_id))

        # Define panel kwargs
        panel_kwargs = {"title_align": "right"}

        # Get display detail by
        display_detail_by = self.display_detail_by

        # Initialize columns
        columns = []

        # Iterate over rows in display detail by
        for row in display_detail_by:

            # Initialize columns
            cols = []

            # Iterate over columns in row
            for field, display in row.items():

                # Get value
                value = getattr(item, field, "N/A")

                # Stringify value
                value = str(value)

                # Add Panel to columns
                cols.append(Panel(value, title=display, **panel_kwargs))

            # Append row of columns
            columns.append(Columns(cols, expand=True))

        # Create renderable
        renderable = RenderGroup(*columns)

        # Pad renderable
        renderable = Padding(renderable, (1, 1))

        # Return renderable
        return renderable

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ DISPLAY DETAIL                                                                 │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def display_detail(self, item_id, interactive=False):
        """ Displays an item detail view using Rich Panels """

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ STATIC                                                                     │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Get detail renderable
        renderable = self.get_detail_renderable(item_id=item_id)

        # Get console
        console = self.console

        # Clear console
        console.clear()

        # Print renderable list view and return
        console.print(renderable, justify="center")

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ INTERACTIVE                                                                │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Return if not interactive
        if not interactive:
            return

        # Initialize while loop
        while True:

            # Get command
            command = console.input(_c.INPUT_TAG)

            # ┌────────────────────────────────────────────────────────────────────────┐
            # │ BASIC COMMANDS                                                         │
            # └────────────────────────────────────────────────────────────────────────┘

            # Handle case of quit
            if command in ["q", "quit"]:
                break

            # ┌────────────────────────────────────────────────────────────────────────┐
            # │ RE-RENDER                                                              │
            # └────────────────────────────────────────────────────────────────────────┘

            # Clear console
            console.clear()

            # Print renderable list view and return
            console.print(renderable, justify="center")
