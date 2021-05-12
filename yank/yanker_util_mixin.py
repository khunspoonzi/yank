# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ GENERAL IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import arrow
import urllib.parse

from functools import reduce

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ PROJECT IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import yank.constants as _c

from yank.target import Target


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ YANKER UTIL MIXIN                                                                  │
# └────────────────────────────────────────────────────────────────────────────────────┘


class YankerUtilMixin:
    """ Yanker Util Mixin """

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ REQUEST                                                                        │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def request(self, url, method, driver_callback=None, solve_captcha_callback=None):
        """ Performs an HTTP request on a Target object """

        # Initialize target object from URL
        target = Target(url=url, yanker=self)

        # Handle case of GET
        if method == _c.GET:

            # Call GET method on target
            target.get(
                driver_callback=driver_callback,
                solve_captcha_callback=solve_captcha_callback,
            )

        # Return target
        return target

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ GET                                                                            │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def get(self, url, driver_callback=None, solve_captcha_callback=None):
        """ Performs an HTTP GET request on a Target object """

        # Make GET request and return target
        return self.request(
            url,
            method=_c.GET,
            driver_callback=driver_callback,
            solve_captcha_callback=solve_captcha_callback,
        )

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
    # │ NOW                                                                            │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def now(self):
        """ Get a UTC timezone aware datetime now object """

        # Return UTC now
        return arrow.utcnow().datetime
