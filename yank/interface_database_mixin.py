# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ GENERAL IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

from datetime import datetime

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ SQLALCHEMY IMPORTS                                                                 │
# └────────────────────────────────────────────────────────────────────────────────────┘

from sqlalchemy import Boolean, DateTime, exists, Float, func, Integer, String

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ PROJECT IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import yank.constants as _c


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ INTERFACE DATABASE MIXIN                                                           │
# └────────────────────────────────────────────────────────────────────────────────────┘


class InterfaceDatabaseMixin:
    """ Interface Database Mixin """

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CONSTANTS                                                                      │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # Type Map
    TYPE_MAP = {
        str: String,
        int: Integer,
        float: Float,
        bool: Boolean,
        datetime: DateTime,
    }

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CLASS ATTRIBUTES                                                               │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # Initialize database session
    db_session = None

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ NEW                                                                            │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def new(self, **kwargs):
        """ A creates a new Item using the SQLAlchemy ORM Item class """

        # Get rid of all kwargs not in field map
        kwargs = {k: v for k, v in kwargs.items() if k in self.field_map}

        # Cast the item fields spplied as kawrgs and return an initialized Item object
        return self.Item(**self.cast_fields(kwargs))

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ GET                                                                            │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def get(self, queryset=None, **kwargs):
        """ Gets an item from the database based in the supplied kwargs """

        # Get queryset
        queryset = queryset or self.db_session.query(self.Item)

        # Return filtered queryset
        return queryset.filter_by(**kwargs).one()

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ COUNT                                                                          │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def count(self):
        """ Returns a count of items in the database """

        # Return count
        return self.db_session.query(func.count(self.Item.id)).scalar()

        """
        For more info on counting with SQL Alchemy:

        https://stackoverflow.com/questions/10822635/get-the-number-of-rows-in-table-
        using-sqlalchemy

        https://stackoverflow.com/questions/14754994/why-is-sqlalchemy-count-much-slower
        -than-the-raw-query
        """

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ EXISTS                                                                         │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def exists(self, **kwargs):
        """
        Returns a boolean of whether an item by the filter kwargs exists in the database
        """

        # Get Item
        Item = self.Item

        # Convert field names to field objects
        kwargs = {getattr(Item, field, None): value for field, value in kwargs.items()}

        # Remove null fields
        kwargs = {k: v for k, v in kwargs.items() if k}

        # Return boolean of whether or not the object exists
        return self.db_session.query(
            exists().where(*[k == v for k, v in kwargs.items()])
        ).scalar()

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ ALL                                                                            │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def all(self):
        """ Returns a queryset of all items in the database """

        # Return a queryset of all items
        return self.db_session.query(self.Item).all()

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ FILTER                                                                         │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def filter(self, queryset=None, display_map=None, tuples=None, **kwargs):
        """
        Returns a filtered queryset of items in the database by the provided kwargs
        """

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ TUPLES                                                                     │
        # └────────────────────────────────────────────────────────────────────────────┘

        # NOTE: A list of tuples can be used instead of kwargs for more complex logic
        # e.g. author__contains=a && author__contains=b
        # Using kwargs, there can only be one author__contains argument as it is a dict

        # Check if tuples
        if tuples:

            # Iterate over tuples
            for field, value in tuples:

                # Get queryset
                queryset = self.filter(
                    queryset=queryset, display_map=display_map, **{field: value}
                )

            # Return queryset
            return queryset

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ KWARGS                                                                     │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Get Item
        Item = self.Item

        # Get field map
        field_map = self.field_map

        # Initialize display map
        display_map = (
            {k.lower(): v for k, v in display_map.items()} if display_map else {}
        )

        # Get queryset
        queryset = queryset or self.db_session.query(Item)

        # Initialize field cache
        field_cache = {}

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ ITERATE OVER KWARGS                                                        │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Iterate over kwargs
        for field, value in kwargs.items():

            # Initialize should negate
            should_negate = False

            # Check if filed starts with tilde
            if field.startswith("~"):

                # Set should negate to True
                should_negate = True

                # Replace tilde
                field = field.replace("~", "", 1).strip()

            # Split field by modifier
            field_split = field.split("__")

            # Separate field from modifier
            field, modifier = (
                field_split if len(field_split) == 2 else (field_split[0], None)
            )

            # Set modifier
            modifier = modifier.lower() if modifier else ""

            # Check if field not in field map
            if field not in field_map:

                # Get field as display
                field = display_map.get(field.lower(), field)

            # Continue if field not in field map
            if field not in field_map:
                continue

            # Get field cast
            field_cast = field_map[field][_c.CAST]

            # Define field is string boolean
            field_is_str = field_cast is str

            # Add field object to field cache
            field_cache[field] = field_cache.get(field, getattr(Item, field))

            # Get field object
            field_obj = field_cache[field]

            # ┌────────────────────────────────────────────────────────────────────────┐
            # │ CAST VALUE                                                             │
            # └────────────────────────────────────────────────────────────────────────┘

            # Check if modifier is not a multiple value operator
            if modifier not in (_c.IN, _c.IIN):

                # Cast value
                value = self.cast_field(field, value)

            # ┌────────────────────────────────────────────────────────────────────────┐
            # │ SUBSTRING                                                              │
            # └────────────────────────────────────────────────────────────────────────┘

            # Handle case of substring
            if (
                modifier
                in (
                    _c.CONTAINS,
                    _c.ICONTAINS,
                    _c.STARTSWITH,
                    _c.ISTARTSWITH,
                    _c.ENDSWITH,
                    _c.IENDSWITH,
                )
                and field_is_str
            ):

                # ┌────────────────────────────────────────────────────────────────────┐
                # │ ARGUMENT STRING                                                    │
                # └────────────────────────────────────────────────────────────────────┘

                # Handle case of contains
                if modifier in (_c.CONTAINS, _c.ICONTAINS):

                    # Wrap argument string in % signs
                    arg_string = f"%{value}%"

                # Otherwise handle case of starts with
                elif modifier in (_c.STARTSWITH, _c.ISTARTSWITH):

                    # Add % sign to end of argument string
                    arg_string = f"{value}%"

                # Otherwise handle case of ends with
                elif modifier in (_c.ENDSWITH, _c.IENDSWITH):

                    # Add % sign to start of argument string
                    arg_string = f"%{value}"

                # ┌────────────────────────────────────────────────────────────────────┐
                # │ QUERY                                                              │
                # └────────────────────────────────────────────────────────────────────┘

                # Handle case of case-sensitive
                if modifier in (_c.CONTAINS, _c.STARTSWITH, _c.ENDSWITH):

                    # Set query using like
                    query = field_obj.like(arg_string)

                # Otherwise handle case of case-insensitive
                elif modifier in (_c.ICONTAINS, _c.ISTARTSWITH, _c.IENDSWITH):

                    # Set query using ilike
                    query = field_obj.ilike(arg_string)

            # ┌────────────────────────────────────────────────────────────────────────┐
            # │ REGEX                                                                  │
            # └────────────────────────────────────────────────────────────────────────┘

            # Otherwise handle case of regex
            elif modifier == _c.REGEX and field_is_str:

                # Define query
                query = field_obj.op("regexp")(value)

            # ┌────────────────────────────────────────────────────────────────────────┐
            # │ IN                                                                     │
            # └────────────────────────────────────────────────────────────────────────┘

            # Otherwise handle case of in
            elif modifier in (_c.IN, _c.IIN):

                # Convert and cast to a list of values
                values = [self.cast_field(field, i.strip()) for i in value.split(",")]

                # Handle case of iin
                if modifier == _c.IIN and field_is_str:

                    # Define query
                    query = func.lower(field_obj).in_([i.lower() for i in values])

                # Otherwise handle normal case
                else:

                    # Define query
                    query = field_obj.in_(values)

            # ┌────────────────────────────────────────────────────────────────────────┐
            # │ EXACT                                                                  │
            # └────────────────────────────────────────────────────────────────────────┘

            # Otherwise handle exact case
            else:

                # Check if modifier is iexact
                if modifier == _c.IEXACT and field_is_str:

                    # Define query
                    query = func.lower(field_obj) == value.lower()

                # Otherwise handle standard exact case
                else:

                    # Define query
                    query = field_obj == value

            # ┌────────────────────────────────────────────────────────────────────────┐
            # │ NEGATE                                                                 │
            # └────────────────────────────────────────────────────────────────────────┘

            # Check if should negate
            if should_negate:

                # Negagte query
                query = ~query

            # ┌────────────────────────────────────────────────────────────────────────┐
            # │ FILTER                                                                 │
            # └────────────────────────────────────────────────────────────────────────┘

            # Filter with query
            queryset = queryset.filter(query)

        # Return filtered queryset
        return queryset

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ SORT                                                                           │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def sort(self, *fields, queryset=None, display_map=None):
        """ Returns a queryset of items sorted by the provided fields """

        # Get Item
        Item = self.Item

        # Initialize display map
        display_map = (
            {k.lower(): v for k, v in display_map.items()} if display_map else {}
        )

        # Initialize new fields list
        _fields = []

        # Iterate over fields
        for field in fields:

            # Initialize ascending boolean
            ascending = True

            # Check if field begins with negative sign
            if field.startswith("-"):

                # Set ascending to False
                ascending = False

                # Remove negative sign from string
                field = field[1:]

            # Get SQL Alchemy field object by field name or display
            field = getattr(
                Item,
                field,
                getattr(Item, display_map[field.lower()], None)
                if field in display_map
                else None,
            )

            # Continue if field is None
            if field is None:
                continue

            # Apply sort direction to field object
            field = field.asc() if ascending is True else field.desc()

            # Add field to fields list
            _fields.append(field)

        # Get queryset
        queryset = queryset or self.db_session.query(Item)

        # Return sorted queryset
        return queryset.order_by(*_fields)
