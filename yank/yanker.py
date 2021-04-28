# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ GENERAL IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import copy
import inspect
import urllib.parse

from functools import reduce

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ PROJECT IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import yank.constants as _c

from yank.browser import Browser
from yank.pliers import Pliers


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ CONSTANTS                                                                          │
# └────────────────────────────────────────────────────────────────────────────────────┘


def constants(cls):
    """
    Dynamically applies selected constants from other utility classes, so that users
    don't have to import import those utility classes to access their constants
    """

    # Iterate over supported browsers
    for browser_slug in Browser.supported_browsers:

        # Set browser constant as class attribute
        setattr(cls, browser_slug.upper(), browser_slug)

    # Return the class
    return cls


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ YANKER                                                                             │
# └────────────────────────────────────────────────────────────────────────────────────┘


@constants
class Yanker:
    """ A base class for custom Yanker classes """

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ PENDING FEATURES                                                               │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # TODO: Enforce transience in the case of driver (new driver each time)
    # TODO: Work on driverless CloudFlare support

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CONSTANTS                                                                      │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # Modes
    SESSION = _c.SESSION
    TRANSIENT = _c.TRANSIENT

    # Interface
    TYPE = _c.TYPE

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

    # Initialize headless to True
    headless = True

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
        headless=None,
    ):
        """ Init Method """

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ MODE                                                                       │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Set mode
        self.mode = mode if mode else self.mode

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
        # │ YANK METHODS                                                               │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Define a yank method wrapper
        def yank_wrapper(method, driver_callback):
            """ Wraps a yank method to handle user-defined class logic """

            # Define wrapped yank method
            def yank_wrapped(target, *args, **kwargs):

                # Get target object from tarket URL
                target = self.pliers.get(target, driver_callback=driver_callback)

                # Return the evaluated method
                return method(target, *args, *kwargs)

            # Return the wrapped yank method
            return yank_wrapped

        # Get yank methods
        yank_methods = inspect.getmembers(self, predicate=inspect.ismethod)
        yank_methods = {k: v for k, v in yank_methods if k.startswith("yank_")}

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

            # Wrap and set yank method
            setattr(self, name, yank_wrapper(method, driver_callback=driver_callback))

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

            # Get headless
            headless = headless if headless is not None else self.headless

            # Initialize and set browser
            self.browser = Browser(default_browser, headless=headless)

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ PLIERS                                                                     │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Initialize pliers
        self.pliers = Pliers(yanker=self)

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
    # │ CLOSE DRIVER                                                                   │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def close_driver(self):
        """ Closes the yanker's active driver """

        # Get driver
        driver = self.browser and self.browser.driver

        # Close driver
        driver and driver.close()

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

    def get_text(self, element, selector, default="N/A", many=False):
        """ Returns the text of a selected element """

        # Get elements
        elements = element.select(selector)

        # Check if many is True
        if many:

            # Return a list of values
            return [e.text for e in elements] if elements else [default]

        # Return the first value
        return elements[0].text if elements else default
