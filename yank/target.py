# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ GENERAL IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import tldextract

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
    # │ INIT METHOD                                                                    │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def __init__(self, url, pliers):
        """ Init Method """

        # Set URL
        self.url = url

        # Set pliers
        self.pliers = pliers

        # Set requester
        self.requester = self.pliers.requester

        # Set driver
        self.driver = self.pliers.driver

        # Set yanker
        self.yanker = pliers.yanker

        # Initialize requests
        self.requests = []

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ GET                                                                            │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def get(self):
        """ Performs an HTTP GET request to the page using its pliers' requester """

        # Get URL
        url = self.url

        # Get yanker
        yanker = self.yanker

        # Determine if should get auto headers
        should_get_auto_headers = yanker.auto_headers and yanker._auto_headers is None

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ DRIVER                                                                     │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Get driver
        driver = self.driver

        # Determine if should use driver
        should_use_driver = driver and should_get_auto_headers

        # Check if driver is not null
        if should_use_driver:

            # Get URL with driver
            driver.get(url)

            # Iterate over driver requests
            for request in driver.requests:

                # Get response
                response = request.response

                # Set request of response
                response.request = request

                # Initialize request object
                request = Request(url)

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

            # Check if pliers mode is transient
            if self.pliers.mode == _c.TRANSIENT:

                # TODO: Implement a dynamic get headers method for users to customize

                # Add default headers to request kwargs
                request_kwargs[_c.HEADERS] = self.pliers.yanker.default_headers

            # Make an HTTP request
            response = self.requester.get(url, **request_kwargs)

            # Set request response
            request.set_response(response)
