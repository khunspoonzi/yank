# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ GENERAL IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import tldextract

from urllib.parse import urlparse

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ PROJECT IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import yank.constants as _c

from yank.request import Request


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ TARGET                                                                             │
# └────────────────────────────────────────────────────────────────────────────────────┘


class Target:
    """ A utility class used to represent a target web page or API endpoint """

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CLASS ATTRIBUTES                                                               │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # Initialize interface to None
    interface = None

    # Initialize cached driver
    _driver = None

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ INIT METHOD                                                                    │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def __init__(self, url, yanker):
        """ Init Method """

        # Set URL
        self.url = url

        # Get parsed URL
        url_parsed = urlparse(url)

        # Set base URL
        self.url_base = self.base_url = f"{url_parsed.scheme}://{url_parsed.netloc}"

        # Set yanker
        self.yanker = yanker

        # Set requester
        self.requester = self.yanker.requester

        # Set browser
        self.browser = self.yanker.browser

        # Set has captcha
        self.has_captcha = False

        # Set captcha solved
        self.captcha_solved = False

        # Initialize requests
        self.requests = []

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ DRIVER                                                                         │
    # └────────────────────────────────────────────────────────────────────────────────┘

    @property
    def driver(self):
        """ Returns an initialized or cached Selenium webdriver instance """

        # Get browser
        browser = self.browser

        # Return None if browser is null
        if not self.browser:
            return None

        # NOTE: Driver is cached so we don't initialize a webdriver instance if the
        # initialized yanker doesn't need it

        # Check if driver is cached
        if self._driver:

            # Return cached driver
            return self._driver

        # Get driver from browser
        driver = browser.driver

        # Cache driver
        self._driver = driver

        # Return driver
        return driver

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ REQUEST                                                                        │
    # └────────────────────────────────────────────────────────────────────────────────┘

    @property
    def request(self):
        """ Returns the request that shares the target's URL """

        # Get target requests
        target_requests = [r for r in self.requests if r.url == self.url]

        # Return None if target requests is null
        if not target_requests:
            return None

        # Get target request
        target_request = target_requests[0]

        # Return target request
        return target_request

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ RESPONSE                                                                       │
    # └────────────────────────────────────────────────────────────────────────────────┘

    @property
    def response(self):
        """ Returns the response of the target request """

        # Return target request's response
        return self.request.response if self.request else None

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ STATUS CODE                                                                    │
    # └────────────────────────────────────────────────────────────────────────────────┘

    @property
    def status_code(self):
        """ Returns the status code of the request that shares the target's URL """

        # Return target request status code
        return self.response.status_code if self.response else None

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ HTML                                                                           │
    # └────────────────────────────────────────────────────────────────────────────────┘

    @property
    def html(self):
        """ Returns the HTML of the target's response object """

        # Return HTML
        return self.response.html

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ JSON                                                                           │
    # └────────────────────────────────────────────────────────────────────────────────┘

    @property
    def json(self):
        """ Returns a JSON dict of the target's response object """

        # Return JSON
        return self.response.json

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ SOUP                                                                           │
    # └────────────────────────────────────────────────────────────────────────────────┘

    @property
    def soup(self):
        """ Returns a HTML BeautifulSoup of the target's response object """

        # Return soup
        return self.response.soup

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ GET                                                                            │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def get(self, driver_callback=None, solve_captcha_callback=None):
        """ Performs an HTTP GET request to the page using its yanker's requester """

        # Get URL
        url = self.url

        # Get yanker
        yanker = self.yanker

        # Determine if should get auto headers
        should_get_auto_headers = yanker.auto_headers and yanker._auto_headers is None

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ DRIVER                                                                     │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Determine if should use driver
        should_use_driver = self.browser and (
            driver_callback or solve_captcha_callback or should_get_auto_headers
        )

        # Check if driver is not null
        if should_use_driver:

            # Get driver
            driver = self.driver

            # TODO: Copy cookies over from session

            # Check if driver callback is not null
            if driver_callback:

                # Check if driver mode is not none and callback has stop when decorator
                if getattr(driver_callback, "has_stop_when", False):

                    # Get quick driver
                    driver_quick = self.browser.driver_quick

                    # Copy cookies from driver to quick driver

                    # Get URL with quick driver
                    driver_quick.get(url)

                    # Copy cookies from quick driver back to driver

                    # Set local driver to quick driver
                    driver = driver_quick

                # Otherwise get URL as usual
                else:

                    # Get URL with driver
                    driver.get(url)

                # Execute driver callback
                driver_callback(driver)

            # Otherwise handle case of no driver callback
            else:

                # Get URL with driver
                driver.get(url)

            # Check if solve captcha callback is not null
            if solve_captcha_callback:

                # TODO: HOW TO MARK AS SOLVED?

                # Pass driver into solve captcha callback
                solve_captcha_callback(driver)

            # Iterate over driver requests
            for request in driver.requests:

                # Get response
                response = request.response

                # Check if response is not None
                if response is not None:

                    # Set request of response
                    response.request = request

                # Initialize request object
                request = Request(url, driver=driver)

                # Set request response
                request.set_response(response)

                # Append request to requests
                self.requests.append(request)

                # ┌────────────────────────────────────────────────────────────────────┐
                # │ AUTO HEADERS                                                       │
                # └────────────────────────────────────────────────────────────────────┘

                # Check if should get auto headers
                if should_get_auto_headers and yanker._auto_headers is None:

                    # Extract registered domain from request URL
                    domain = tldextract.extract(request.url).registered_domain

                    # Check if registered domain is in the target URL
                    if domain in url:

                        # Get auto headers
                        _auto_headers = request.headers

                        # Update auto headers by default headers
                        _auto_headers.update(yanker.default_headers)

                        # Set auto headers cache to request headers
                        yanker._auto_headers = request.headers

                        # Set default headers
                        yanker.default_headers = _auto_headers

                        # Break here
                        break

            # Check if mode is session
            if self.yanker.mode == _c.SESSION:

                # Get driver user agent
                driver_user_agent = driver.execute_script("return navigator.userAgent;")

                # Update session user agent
                self.requester.headers.update({"User-Agent": driver_user_agent})

                # Get driver cookies
                driver_cookies = driver.get_cookies()

                # Update session cookies
                self.requester.cookies.update(
                    {c["name"]: c["value"] for c in driver_cookies}
                )

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ REQUESTER                                                                  │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Otherwise handle no driver
        else:

            # Initialize request object
            request = Request(url)

            # Append request to requests
            self.requests.append(request)

            # Initialize request kwargs
            request_kwargs = {}

            # Check if yanker mode is transient
            if self.yanker.mode == _c.TRANSIENT:

                # TODO: Implement a dynamic get headers method for users to customize

                # Add default headers to request kwargs
                request_kwargs[_c.HEADERS] = self.yanker.default_headers

            # Make an HTTP request
            response = self.requester.get(url, **request_kwargs)

            # Set request response
            request.set_response(response)

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ FILTER_REQUESTS                                                                │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def filter_requests(self, **kwargs):
        """ Filters the target's requests by given keyword arguments """

        # Get requests
        requests = self.requests

        # Filter requests
        requests = [
            r
            for r in requests
            if all([getattr(r, k, None) == v for k, v in kwargs.items()])
        ]

        # Return requests
        return requests
