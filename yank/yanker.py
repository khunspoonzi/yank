# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ GENERAL IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import arrow
import copy
import inspect
import re
import requests
import urllib.parse

from functools import reduce

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ SQL ALCHEMY IMPORTS                                                                │
# └────────────────────────────────────────────────────────────────────────────────────┘

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ PROJECT IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import yank.constants as _c

from yank.browser import Browser
from yank.interface import Interface
from yank.target import Target


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ DATABASE                                                                           │
# └────────────────────────────────────────────────────────────────────────────────────┘

# Initialize base class
DBBase = declarative_base()


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ YANKER                                                                             │
# └────────────────────────────────────────────────────────────────────────────────────┘


class Yanker:
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

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CUSTOMIZABLE CLASS ATTRIBUTES                                                  │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # Initialize mode to transient
    mode = TRANSIENT

    # Initialize start URLs to None
    start_urls = None

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

    # Initialize Browser class so that users can easily access its constants
    Browser = Browser

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
        has_driver_callback = self.wrap_methods()

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ BROWSER AND DRIVER                                                         │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Set browser to None
        self.browser = None

        # Determine if Selenium driver is required
        driver_is_required = self.auto_headers or has_driver_callback

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
    # │ REQUEST                                                                        │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def request(self, url, method, driver_callback=None):
        """ Performs an HTTP request on a Target object """

        # Initialize target object from URL
        target = Target(url=url, yanker=self)

        # Handle case of GET
        if method == _c.GET:

            # Call GET method on target
            target.get(driver_callback=driver_callback)

        # Return target
        return target

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ GET                                                                            │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def get(self, url, driver_callback=None):
        """ Performs an HTTP GET request on a Target object """

        # Make GET request and return target
        return self.request(url, method=_c.GET, driver_callback=driver_callback)

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CLOSE DRIVER                                                                   │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def close_driver(self):
        """ Closes the yanker's active driver """

        # Get browser
        browser = self.browser

        # Get drivers
        driver = browser and browser.driver
        driver_quick = browser and browser._driver_quick

        # Close drivers
        driver and driver.quit()
        driver_quick and driver_quick.quit()

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ URLJOIN                                                                        │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def urljoin(self, *args, params=None):
        """ Joins a series of URL components """

        # Get joined URL from the supplied components
        url = reduce(urllib.parse.urljoin, args).rstrip("/")

        # Convert params to a list of tuples
        params = params.items() if type(params) is dict else params

        # Get quote function
        q = urllib.parse.quote_plus

        # Convert params to list
        params = [f"{q(key)}={q(val)}" for key, val in params] if params else []

        # Convert params to string
        params = "&".join(params)

        # Check if params is not null
        if params:

            # Append params to url
            url += "?" + params

        # Return the joined URL
        return url

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ GET TEXT                                                                       │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def get_text(self, element, selector, default="", many=False):
        """ Returns the text of a selected element """

        # Get elements
        elements = element.select(selector)

        # Check if many is True
        if many:

            # Return a list of values
            return [e.text for e in elements] if elements else [default]

        # Return the first value
        return elements[0].text if elements else default

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ NOW                                                                            │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def now(self):
        """ Get a UTC timezone aware datetime now object """

        # Return UTC now
        return arrow.utcnow().datetime

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ TABLES                                                                         │
    # └────────────────────────────────────────────────────────────────────────────────┘

    @property
    def tables(self):
        """ Returns a dict of table objects in the database """

        # Return tables
        return []
        # return db_meta.tables

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ TABLE NAMES                                                                    │
    # └────────────────────────────────────────────────────────────────────────────────┘

    @property
    def table_names(self):
        """ Returns a list of table names in the database """

        # Return table names
        return list(self.tables.keys())

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ WRAP METHODS                                                                   │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def wrap_methods(self):
        """ Wraps user-defined methods in existing Yanker utility methods """

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ WRAPPER                                                                    │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Define a method wrapper
        def wrapper(method, driver_callback, clean_callback):
            """ Wraps a yank method to handle user-defined class logic """

            # Define wrapped method
            def wrapped(target, *args, **kwargs):

                # ┌────────────────────────────────────────────────────────────────────┐
                # │ MAKE REQUEST                                                       │
                # └────────────────────────────────────────────────────────────────────┘

                # Get target object from tarket URL
                target = self.get(target, driver_callback=driver_callback)

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
                        item = interface.Item(**item)

                        self.db_session.add(item)
                        self.db_session.commit()

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

            # Wrap and set yank method
            setattr(
                self,
                name,
                wrapper(
                    method,
                    driver_callback=driver_callback,
                    clean_callback=clean_callback,
                ),
            )

        # Return has driver callback
        return has_driver_callback

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

            # Initialize an interface
            interface = Interface(DBBase, db_table_name=db_table_name, **kwargs)

            # Define wrapper
            def wrapper(instance, target, *args, **kwargs):

                # Set interface on target
                target.interface = interface

                # Execute original method
                return method(instance, target, *args, **kwargs)

            # Return wrapper
            return wrapper

        # Return the decorator
        return decorator
