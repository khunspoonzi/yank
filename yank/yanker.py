# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ GENERAL IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import copy
import inflect
import inspect
import random
import re
import requests
import time

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ SQL ALCHEMY IMPORTS                                                                │
# └────────────────────────────────────────────────────────────────────────────────────┘

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ PROJECT IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import yank.constants as _c

from yank.browser import Browser
from yank.exceptions import SessionLimitReached
from yank.interface import Interface
from yank.yanker_display_mixin import YankerDisplayMixin
from yank.yanker_util_mixin import YankerUtilMixin


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ INFLECTOR                                                                          │
# └────────────────────────────────────────────────────────────────────────────────────┘

# Initialize inflector for singular / plural conversions
inflector = inflect.engine()

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ DATABASE                                                                           │
# └────────────────────────────────────────────────────────────────────────────────────┘

# Initialize base class
DBBase = declarative_base()


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ YANKER                                                                             │
# └────────────────────────────────────────────────────────────────────────────────────┘


class Yanker(YankerDisplayMixin, YankerUtilMixin):
    """ A base class for custom Yanker classes """

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ PENDING FEATURES                                                               │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # TODO: Implement a dynamic get headers method for users to customize
    # TODO: Enforce transience in the case of driver (new driver each time)
    # TODO: Implement session transfer from requester to driver (not done yet)
    # TODO: Auto set driver mode to quick if all yank methods have a driver method with
    #       a stop when decorator
    # TODO: Allow for sharing of single interface between methods
    # TODO: Implement skip by URL as a standalone decorator
    # TODO: Truncate list view if row count is huge
    # TODO: Improve list view reset to be able to choose what to reset

    # TODO: Improve session limits with non-items
    # TODO: Improve uniqueness handling
    # TODO: Build a CSV / XLSX exporter
    # TODO: Figure out how to share an interface between Yankers or Merger
    # TODO: Implement a hardcoded auto header as first try
    # TODO: Get base URL from current target
    # TODO: Fix missing taget.response when driver requests is False
    # TODO: Implement batches as a column in database for freelance work
    # TODO: Implement ability to not define start URLs
    # TODO: Add ID to columns in display table
    # TODO: Do not initialize database if not interface / (history)?
    # TODO: Implement generic captcha detector

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CONSTANTS                                                                      │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # Modes
    SESSION = _c.SESSION
    TRANSIENT = _c.TRANSIENT

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CLASS ATTRIBUTES                                                               │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # Define requester
    requester = requests

    # Initialize Browser class so that users can easily access its constants
    Browser = Browser

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CUSTOMIZABLE CLASS ATTRIBUTES                                                  │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # Initialize mode to transient
    mode = TRANSIENT

    # Initialize start URLs to None
    start_urls = None

    # Initialize throttle to None
    throttle_ms = None

    # Initialize auto headers to False
    auto_headers = False

    # Initialize default headers to None
    default_headers = None

    # Initialize default browser
    default_browser = Browser.CHROME

    # Initialize driver mode to normal
    driver_mode = Browser.NORMAL

    # Initialize driver headless to False
    driver_headless = False

    # Initialize driver requests to False
    driver_requests = False

    # Initialize database name to None
    db_name = None

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ INIT METHOD                                                                    │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def __init__(
        self,
        start_urls=None,
        mode="",
        auto_headers=None,
        default_headers=None,
        default_browser="",
        driver_mode=None,
        driver_headless=None,
        driver_requests=None,
        db_name=None,
    ):
        """ Init Method """

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ INFLECTOR                                                                  │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Set inflector
        self.inflector = inflector

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ MODE                                                                       │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Set mode
        self.mode = mode if mode else self.mode

        # Check if mode is session
        if self.mode == _c.SESSION:

            # Set requester to a new requests session
            self.requester = requests.Session()

            # Set default headers
            self.requester.headers.update(self.default_headers)

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ DATABASE                                                                   │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Initialize tables to empty dict
        self.tables = {}

        # Set database name
        self.db_name = db_name or self.db_name

        # Check if database name is None
        if self.db_name is None:

            # Get class name
            class_name = self.__class__.__name__

            # Set database name as snake case version of class name
            self.db_name = re.sub(r"(?<!^)(?=[A-Z])", "_", class_name).lower()

        # Initialize database engine
        self.db_engine = create_engine(f"sqlite:///{self.db_name}.db")

        # Register exponent function with SQLite
        @event.listens_for(self.db_engine, "connect")
        def create_functions(dbapi_connection, connection_record):
            dbapi_connection.create_function("pow", 2, lambda x, y: x ** y)

        # Create tables
        DBBase.metadata.create_all(self.db_engine)

        # Make a database session class
        DBSession = sessionmaker(bind=self.db_engine)

        # Initialize database session
        self.db_session = DBSession()

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ START URLS                                                                 │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Initialize start URLs from class attribute
        self.start_urls = start_urls or self.start_urls or []

        # Check if start URLs is a string
        if type(self.start_urls) is str:

            # Convert to list
            self.start_urls = [self.start_urls]

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ HEADERS                                                                    │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Set auto headers
        self.auto_headers = (
            auto_headers if auto_headers is not None else self.auto_headers
        )

        # Initialize auto headers cache
        self._auto_headers = None

        # Get default headers
        default_headers = self.default_headers

        # Initialize default headers
        self.default_headers = copy.deepcopy(default_headers) if default_headers else {}

        # Check if additional default headers were passed in
        if default_headers:

            # Update the instance's default headers
            self.default_headers.update(default_headers)

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ WRAP METHODS                                                               │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Call wrap methods
        # This will determine whether the user has defined a driver callback method
        has_driver_callback, has_solve_captcha_callback = self.wrap_methods()

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ BROWSER AND DRIVER                                                         │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Set browser to None
        self.browser = None

        # Determine if Selenium driver is required
        driver_is_required = (
            self.auto_headers or has_driver_callback or has_solve_captcha_callback
        )

        # Check if driver is required
        if driver_is_required:

            # Get default browser and supported browsers
            default_browser = default_browser or self.default_browser

            # Get driver mode
            driver_mode = driver_mode if driver_mode is not None else self.driver_mode

            # Get driver headless
            driver_headless = (
                driver_headless if driver_headless is not None else self.driver_headless
            )

            # Get driver requests
            driver_requests = (
                driver_requests if driver_requests is not None else self.driver_requests
            )

            # Initialize and set browser
            self.browser = Browser(
                default_browser,
                driver_mode=driver_mode,
                driver_headless=driver_headless,
                driver_requests=driver_requests,
            )

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ YANK                                                                           │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def yank(self):
        """ Runs the yanker on its start URLs """

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ ITERATE OVER START URLS                                                    │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Iterate over start URLs
        for start_url in self.start_urls:

            # Initialize try-except block
            try:

                # Call yank start method on start URL
                self.yank_start(start_url)

            # Except any exception
            except SessionLimitReached:

                # Pass onto end of method
                pass

            # Except any exception
            except Exception:

                # Close driver to avoid lingering headless browser instances
                self.close_driver()

                # Re-raise the exception
                raise

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ CLOSE DRIVER                                                               │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Close driver
        self.close_driver()

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ YANK START                                                                     │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def yank_start(self, target):
        """ The action performed on each of the yanker's start URLs """

        # Raise NotImplementedError
        raise

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ INTERFACE                                                                      │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def interface(**kwargs):
        """
        Registers an interface with a yank method
        This effectively marks the method's return value to be commited to the daatabase
        """

        # Define decorator
        def decorator(method):

            # Get method name
            method_name = method.__name__

            # Get database table name from method name
            db_table_name = method_name.replace("yank_", "")

            # Convert database table name to singular form
            db_table_name = inflector.singular_noun(db_table_name) or db_table_name

            # Convert database table name to lower- snake-case
            db_table_name = db_table_name.lower().replace(" ", "")

            # Initialize an interface
            interface = Interface(DBBase, db_table_name=db_table_name, **kwargs)

            # Define wrapper
            def wrapper(instance, target, *args, **kwargs):

                # Set interface on target
                target.interface = interface

                # Execute original method
                return method(instance, target, *args, **kwargs)

            # Add the interface as an attribute on the wrapped method
            wrapper.interface = interface

            # Return wrapper
            return wrapper

        # Return the decorator
        return decorator

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ WRAP METHODS                                                                   │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def wrap_methods(self):
        """ Wraps user-defined methods in existing Yanker utility methods """

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ WRAPPER                                                                    │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Define a method wrapper
        def wrapper(
            method,
            driver_callback,
            clean_callback,
            has_captcha_callback,
            solve_captcha_callback,
        ):
            """ Wraps a yank method to handle user-defined class logic """

            # ┌────────────────────────────────────────────────────────────────────────┐
            # │ GET INTERFACE                                                          │
            # └────────────────────────────────────────────────────────────────────────┘

            # Get interface from method if it exists
            interface = getattr(method, "interface", None)

            # Check if interface is not null
            if interface:

                # Add instance session to interface
                interface.db_session = self.db_session

                # Get database table name
                db_table_name = interface.db_table_name

                # Convert database table name to Pascal Case
                interface_name = "".join(
                    [
                        w.title() if len(w) > 2 else w.upper()
                        for w in db_table_name.split("_")
                    ]
                )

                # Set interface name
                interface.name = interface_name

                # Add interface as a "table" accessible on the yanker instance
                setattr(self, interface_name, interface)

                # Add interface to tables dict
                self.tables[db_table_name] = interface

            # Define wrapped method
            def wrapped(target, *args, **kwargs):

                # ┌────────────────────────────────────────────────────────────────────┐
                # │ PRE-REQUEST FILTERS                                                │
                # └────────────────────────────────────────────────────────────────────┘

                # Get interface from method if it exists
                interface = getattr(method, "interface", None)

                # Check if interface is not null
                if interface:

                    # ┌────────────────────────────────────────────────────────────────┐
                    # │ SESSION LIMIT                                                  │
                    # └────────────────────────────────────────────────────────────────┘

                    # Get interface session limit
                    session_limit = interface.session_limit

                    # Check if interface session count has reached session limit
                    if session_limit and interface.session_count >= session_limit:

                        # Raise SessionLimitReached
                        raise SessionLimitReached

                    # ┌────────────────────────────────────────────────────────────────┐
                    # │ SKIP BY URL                                                    │
                    # └────────────────────────────────────────────────────────────────┘

                    # Get skip by URL boolean
                    skip_by_url = interface.skip_by_url

                    # Check if should skip by URL
                    if skip_by_url:

                        # Return None if item with target URL exists
                        if interface.exists(url=target):
                            return None

                # Otherwise handle case of method decorator
                else:

                    pass

                # ┌────────────────────────────────────────────────────────────────────┐
                # │ MAKE REQUEST                                                       │
                # └────────────────────────────────────────────────────────────────────┘

                # Get throttle ms
                throttle_ms = self.throttle_ms

                # Check if throttle ms is a list or tuple
                if type(throttle_ms) in [list, tuple]:

                    # Generate a random integer between min and max
                    throttle_ms = random.randint(min(throttle_ms), max(throttle_ms))

                # Implement sleep to throttle the request
                time.sleep(throttle_ms / 1000)

                # Get target object from tarket URL
                target = self.get(target, driver_callback=driver_callback)

                # Check if has captcha callback
                if has_captcha_callback:

                    # Check if target has captcha
                    if has_captcha_callback(target):

                        # Set target has captcha
                        target.has_captcha = True

                        # Set target captcha solved to False
                        target.captcha_solved = False

                        # Check if solve captcha callback
                        if solve_captcha_callback:

                            # Get the target with captcha callback
                            target = self.get(
                                target.url,
                                driver_callback=driver_callback,
                                solve_captcha_callback=solve_captcha_callback,
                            )

                            # Get target object from tarket URL
                            target = self.get(
                                target.url, driver_callback=driver_callback
                            )

                # Get result
                result = method(target, *args, *kwargs)

                # ┌────────────────────────────────────────────────────────────────────┐
                # │ CLEAN RESULT                                                       │
                # └────────────────────────────────────────────────────────────────────┘

                # Check if clean callback exists
                if clean_callback:

                    # Pass result through clean callback
                    result = clean_callback(target.interface, result) or result

                # ┌────────────────────────────────────────────────────────────────────┐
                # │ CAST VALUES                                                        │
                # └────────────────────────────────────────────────────────────────────┘

                # Get interface
                interface = target.interface

                # Check if interface is not None
                if interface is not None:

                    # Convert result to list if not list
                    result = result if type(result) in [list, tuple] else [result]

                    # Iterate over result
                    for item in result:

                        # Continue if item is None
                        if item is None:
                            continue

                        # Add URL to item
                        item[_c.URL] = target.url

                        # Add timestamp to item
                        item[_c.YANKED_AT] = self.now()

                        # Convert to ORM item
                        item = interface.new(**item)

                        # Add anc commit item to database
                        self.db_session.add(item)
                        self.db_session.commit()

                        # Increment interface session count
                        interface.session_count += 1

                # Return the evaluated method
                return result

            # Return the wrapped method
            return wrapped

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ WRAP METHODS                                                               │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Get all methods
        all_methods = inspect.getmembers(self, predicate=inspect.ismethod)
        all_methods = {k: v for k, v in all_methods}

        # Get yank methods
        yank_methods = {k: v for k, v in all_methods.items() if k.startswith("yank_")}

        # Initialize has driver callback boolean
        has_driver_callback = False

        # Initialize has solve captcha callback boolean
        has_solve_captcha_callback = False

        # Iterate over yank methods
        for name, method in yank_methods.items():

            # Continue if suffixed method
            if "__" in name:
                continue

            # Get driver callback
            driver_callback = yank_methods.get(f"{name}__driver")

            # Check if driver callback is not null
            if driver_callback:

                # Set has driver callback to True
                has_driver_callback = True

            # Get clean callback
            clean_callback = all_methods.get(name.replace("yank_", "clean_", 1))

            # Get has captcha callback
            has_captcha_callback = yank_methods.get(f"{name}__has_captcha")

            # Get solve captcha callback
            solve_captcha_callback = yank_methods.get(f"{name}__solve_captcha")

            # Check if solve captcha callback is not null
            if solve_captcha_callback:

                # Set has has solve captcha callback to True
                has_solve_captcha_callback = True

            # Wrap and set yank method
            setattr(
                self,
                name,
                wrapper(
                    method,
                    driver_callback=driver_callback,
                    clean_callback=clean_callback,
                    has_captcha_callback=has_captcha_callback,
                    solve_captcha_callback=solve_captcha_callback,
                ),
            )

        # Return callback booleans
        return has_driver_callback, has_solve_captcha_callback
