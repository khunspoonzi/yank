# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ GENERAL IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import math

from datetime import datetime

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ SQLALCHEMY IMPORTS                                                                 │
# └────────────────────────────────────────────────────────────────────────────────────┘

from sqlalchemy import Column, func, Integer
from sqlalchemy.ext.hybrid import hybrid_property

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ PROJECT IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import yank.constants as _c

from yank.interface_database_mixin import InterfaceDatabaseMixin
from yank.interface_display_mixin import InterfaceDisplayMixin


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ INTERFACE                                                                          │
# └────────────────────────────────────────────────────────────────────────────────────┘


class Interface(InterfaceDatabaseMixin, InterfaceDisplayMixin):
    """ A utility class for managing the schema of yanked data """

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CONSTANTS                                                                      │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # Interface
    CAST = _c.CAST
    DISPLAY = _c.DISPLAY
    NULL = _c.NULL
    RANK = _c.RANK
    UNIQUE = _c.UNIQUE
    WEIGHT = _c.WEIGHT

    # Fields
    ID = _c.ID
    URL = _c.URL
    YANKED_AT = _c.YANKED_AT

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CLASS ATTRIBUTES                                                               │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # Initialize name to empty string
    name = ""

    # Initialize skip by URL to False
    skip_by_url = False

    # Initialize session limit to None
    session_limit = None

    # Initialize session count to 0
    session_count = 0

    # Initialize display list by to None
    display_list_by = None

    # Initialize list display map to None
    list_display_map = None

    # Initialize display detail by to None
    display_detail_by = None

    # Initialize detail display map to None
    detail_display_map = None

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ INIT METHOD                                                                    │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def __init__(self, DBBase, db_table_name, inflector, **kwargs):
        """ Init Method """

        # Get common constants
        CAST = self.CAST
        DISPLAY = self.DISPLAY
        RANK = self.RANK
        UNIQUE = self.UNIQUE
        WEIGHT = self.WEIGHT

        # Set table name
        self.db_table_name = db_table_name

        # Initialize inflector
        self.inflector = inflector

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ CUSTOM ATTRIBUTES                                                          │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Get attributes
        attributes = {k: v for k, v in kwargs.items() if k.startswith("__")}

        # Iterate over attributes
        for k, v in attributes.items():

            # Set attribute
            setattr(self, k.replace("__", "", 1).strip(), v)

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ FIELD MAP                                                                  │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Initialize field map
        field_map = {_c.ID: {_c.CAST: int, _c.DISPLAY: "ID"}}

        # Add kwargs to field map
        field_map = {
            **field_map,
            **{k: v for k, v in kwargs.items() if k not in attributes},
        }

        # Add yanked at and URL to field map
        field_map[self.URL] = {CAST: str, DISPLAY: "URL"}
        field_map[self.YANKED_AT] = datetime

        # Normalize the structure of the field map
        field_map = {
            k: (v if type(v) is dict else {CAST: v}) for k, v in field_map.items()
        }

        # Set field map
        self.field_map = field_map

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ DEFAULTS                                                                   │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Compute total weight
        weight_total = sum(
            [abs(info.get(WEIGHT, 0)) for info in self.field_map.values()]
        )

        # Iterate over field map
        for field, info in self.field_map.items():

            # Define display
            info[DISPLAY] = info.get(DISPLAY) or " ".join(
                [w.title() for w in field.split("_")]
            )

            # Get weight
            weight = info.get(WEIGHT) or None

            # Determine if weight is reversed
            weight_is_reversed = weight < 0 if weight else False

            # Normalize weight according to total
            weight = abs(weight) / weight_total if weight else None

            # Reverse weight if necessary
            weight = weight * -1 if weight_is_reversed else weight

            # Set weight
            info[WEIGHT] = weight

        # Get weighted columns
        weighted_columns = {
            field: info[WEIGHT]
            for field, info in self.field_map.items()
            if info[WEIGHT] is not None
        }

        # Get positive weighted columns
        weighted_columns_positive = {k: v for k, v in weighted_columns.items() if v > 0}

        # Get negative weighted columns
        weighted_columns_negative = {k: v for k, v in weighted_columns.items() if v < 0}

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ COLUMNS                                                                    │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Define columns decorator
        def columns(cls):
            """ Dynamically sets SQLAlchemy columns on a target ORM class """

            # Iterate over field map
            for field, info in self.field_map.items():

                # Continue if field is ID (created manually)
                if field == _c.ID:
                    continue

                # Get column type
                ColType = self.TYPE_MAP[info[CAST]]

                # Get unique
                unique = info.get(UNIQUE, False)

                # Set class attribute
                setattr(cls, field, Column(ColType, unique=unique))

            # Define rank
            @hybrid_property
            def rank(self):

                # Get rank
                rank = math.prod(
                    [1]
                    + [
                        getattr(self, field) ** weight
                        for field, weight in weighted_columns_positive.items()
                    ]
                ) / math.prod(
                    [1]
                    + [
                        getattr(self, field) ** abs(weight)
                        for field, weight in weighted_columns_negative.items()
                    ]
                )

                # Return rank
                return rank

            # Define rank expression
            @rank.expression
            def rank(cls):

                # Get rank
                rank = math.prod(
                    [1]
                    + [
                        func.pow(getattr(cls, field), weight)
                        for field, weight in weighted_columns_positive.items()
                    ]
                ) / math.prod(
                    [1]
                    + [
                        func.pow(getattr(cls, field), abs(weight))
                        for field, weight in weighted_columns_negative.items()
                    ]
                )
                return rank

            # Set rank property
            setattr(cls, RANK, rank)

            # Return the ORM class
            return cls

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ ITEM                                                                       │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Define Item ORM class
        @columns
        class Item(DBBase):
            """ The ORM class that will house the user-defined columns """

            # Set table name
            __tablename__ = self.db_table_name

            # Set ID as primary key
            id = Column(Integer, primary_key=True)

        # Set Item class on interface object
        self.Item = Item

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ LIST DISPLAY SETTINGS                                                      │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Initialize list display map
        self.list_display_map = {self.field_map[_c.ID][_c.DISPLAY]: _c.ID}

        # Check if display list by is defined
        if self.display_list_by:

            # Iterate over display list by
            for item in self.display_list_by:

                # Initialize display
                display = None

                # Check if item is a list or tuple
                if type(item) in (list, tuple):

                    # Unpack field and display
                    field, display = item

                # Otherwise handle string
                else:

                    # Set field
                    field = item

                # Continue if field not in field map
                if field not in self.field_map:
                    continue

                # Set display
                display = display or self.field_map[field][_c.DISPLAY]

                # Add to display map
                self.list_display_map[display] = field

        # Otherwise handle case of undefined display list by
        else:

            # Iterate over the first five items of the field map
            for field in list(self.field_map.keys())[:5]:

                # Add to display map
                self.list_display_map[self.field_map[field][_c.DISPLAY]] = field

        # Convert display list by into a dictionary
        self.display_list_by = {v: k for k, v in self.list_display_map.items()}

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ DETAIL DISPLAY SETTINGS                                                    │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Initialize detail display map
        self.detail_display_map = {}

        # Initialize new display detail by
        _display_detail_by = []

        # Check if display detail by is defined
        if self.display_detail_by:

            # Iterate over rows in display detail by
            for row in self.display_detail_by:

                # Initialize columns
                cols = {}

                # Iterate over columns in row
                for col in row:

                    # Initialize display
                    display = None

                    # Check if item is a list or tuple
                    if type(col) in (list, tuple):

                        # Unpack field and display
                        field, display = col

                    # Otherwise handle string
                    else:

                        # Set field
                        field = col

                    # Continue if field not in field map
                    if field not in self.field_map:
                        continue

                    # Set display
                    display = display or self.field_map[field][_c.DISPLAY]

                    # Add column to columns
                    cols[field] = display

                    # Add to display map
                    self.detail_display_map[display] = field

                # Add columns to new display detail by
                _display_detail_by.append(cols)

        # Otherwise handle case of undefined display detail by
        else:

            # Initialize columns
            cols = {}

            # Get detail display fields as first ten fields
            detail_display_fields = list(self.field_map.keys())[:10]

            # Remove URL and yanked at from fields
            detail_display_fields = [
                f for f in detail_display_fields if f not in (_c.URL, _c.YANKED_AT)
            ]

            # Iterate over detail display fields
            for i, field in enumerate(detail_display_fields, 1):

                # Get display
                display = self.field_map[field][_c.DISPLAY]

                # Add column to columns
                cols[field] = display

                # Add to display map
                self.detail_display_map[display] = field

                # Check if index is divisible by two or is last
                if i % 2 == 0 or i == len(detail_display_fields):

                    # Add columns to new display detail by
                    _display_detail_by.append(cols)

                    # Reset columns
                    cols = {}

            # Get URL display
            url_display = self.field_map[_c.URL][_c.DISPLAY]

            # Get yanked at display
            yanked_at_display = self.field_map[_c.YANKED_AT][_c.DISPLAY]

            # Add to display map
            self.detail_display_map[url_display] = _c.URL
            self.detail_display_map[yanked_at_display] = _c.YANKED_AT

            # Add URL and yanked at as a pair at the end
            _display_detail_by.append(
                {_c.URL: url_display, _c.YANKED_AT: yanked_at_display}
            )

        # Redefine display detail by
        self.display_detail_by = _display_detail_by

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CAST FIELDS                                                                    │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def cast_fields(self, item_dict, display_map=None):
        """ Casts a dict of item fields according to a the interface's field map """

        # Initialize display map
        display_map = (
            {k.lower(): v for k, v in display_map.items()} if display_map else {}
        )

        # Convert fields from display
        item_dict = {
            field
            if field in self.field_map
            else display_map.get(field.lower(), field): value
            for field, value in item_dict.items()
        }

        # Cast item dict
        item_dict = {
            field: self.cast_field(field, value) for field, value in item_dict.items()
        }

        # Return the item dict
        return item_dict

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CAST FIELD                                                                     │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def cast_field(self, field, value):
        """ Casts a value according to a field in the interface's field map """

        # Get field map
        field_map = self.field_map

        # Return value if field not in field map
        if field not in field_map:
            return value

        # Check if value is None
        if value is None:

            # Get null boolean
            null = field_map[field].get(self.NULL, False)

            # Check if null is permitted
            if null:

                # Return the value
                return value

        # Get value type
        value_type = type(value)

        # Check if value is a list
        if value_type is list:

            # Return a comma separated list
            # Currently no support for array structures in database
            return "; ".join([str(i).replace(";", ",") for i in value])

        # Get to type
        to_type = field_map[field][self.CAST]

        # Check if to type is int
        if to_type is int:

            # Check if value is str
            if value_type is str:

                # Remove common unwanted characters
                value = value.replace(",", "")

        # Handle case of datetime
        elif to_type is datetime:

            # Assert value is datetime
            assert value_type is datetime, f"{field} is not a valid datetime"

        # Cast value to appropriate type
        value = to_type(value)

        # Return value
        return value
