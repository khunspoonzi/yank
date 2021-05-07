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

    def filter(self, **kwargs):
        """
        Returns a filtered queryset of items in the database by the provided kwargs
        """

        # Return filtered queryset
        return self.db_session.query(self.Item).filter_by(**kwargs)