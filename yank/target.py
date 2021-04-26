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
        return self.request.response

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ STATUS CODE                                                                    │
    # └────────────────────────────────────────────────────────────────────────────────┘

    @property
    def status_code(self):
        """ Returns the status code of the request that shares the target's URL """

        # Return target request status code
        return self.target_request.status_code

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ JSON                                                                           │
    # └────────────────────────────────────────────────────────────────────────────────┘

    @property
    def json(self):
        """ Returns a JSON dict of the response object """

        try:
            # Return JSON data
            return self.response.json()

        except AttributeError:

            # Return None
            return None

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ GET                                                                            │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def get(self, driver_callback=None):
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
        should_use_driver = driver and (driver_callback or should_get_auto_headers)

        # Check if driver is not null
        if should_use_driver:

            # Get URL with driver
            driver.get(url)

            # Check if driver callback is not null
            if driver_callback:

                # Execute driver callback
                driver_callback(driver)

            # Iterate over driver requests
            for request in driver.requests:

                # Get response
                response = request.response

                # Check if response is not None
                if response is not None:

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
