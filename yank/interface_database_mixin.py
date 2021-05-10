# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ GENERAL IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

from datetime import datetime

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ SQLALCHEMY IMPORTS                                                                 │
# └────────────────────────────────────────────────────────────────────────────────────┘

from sqlalchemy import DateTime, exists, Float, func, Integer, String


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

        # Cast the item fields spplied as kawrgs and return an initialized Item object
        return self.Item(**self.cast_fields(kwargs))

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

    def filter(self, queryset=None, display_map=None, **kwargs):
        """
        Returns a filtered queryset of items in the database by the provided kwargs
        """

        # Get Item
        Item = self.Item

        # Get field map
        field_map = self.field_map

        # Initialize display map
        display_map = {k.lower(): v for k, v in display_map.items()} or {}

        # Initialize kwargs
        _kwargs = {}

        # Iterate over kwargs
        for field, value in kwargs.items():

            # Check if field not in field map
            if field not in field_map:

                # Get field as display
                field = display_map.get(field.lower(), field)

            # Continue if field not in field map
            if field not in field_map:
                continue

            # Add field to kwargs
            _kwargs[field] = value

        # Get queryset
        queryset = queryset or self.db_session.query(Item)

        # Return filtered queryset
        return queryset.filter_by(**_kwargs)

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ SORT                                                                           │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def sort(self, *fields, queryset=None, display_map=None):
        """ Returns a queryset of items sorted by the provided fields """

        # Get Item
        Item = self.Item

        # Initialize display map
        display_map = {k.lower(): v for k, v in display_map.items()} or {}

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
