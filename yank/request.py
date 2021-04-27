# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ SELENIUM IMPORTS                                                                   │
# └────────────────────────────────────────────────────────────────────────────────────┘

from seleniumwire.request import HTTPHeaders

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ PROJECT IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

from yank.response import Response


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ REQUEST                                                                            │
# └────────────────────────────────────────────────────────────────────────────────────┘


class Request:
    """ A utility class used to represent a single HTTP request """

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ INIT METHOD                                                                    │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def __init__(self, url, driver=None):
        """ Init Method """

        # Set URL
        self.url = url

        # Set driver
        self.driver = driver

        # Initialize headers to None
        self.headers = None

        # Initialize response to None
        self.response = None

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ SET RESPONSE                                                                   │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def set_response(self, response):
        """ Sets a response to the current request object """

        # Return if response is None
        if response is None:
            return

        # Get headers
        headers = response.request.headers

        # Check if headers is a Seleniumwire HTTPHeader object
        if type(headers) is HTTPHeaders:

            # Convert headers to dict
            headers = dict(headers)

        # Set request headers
        self.headers = headers

        # Set response
        self.response = Response(request=self, response=response)
