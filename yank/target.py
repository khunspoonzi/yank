# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ PROJECT IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

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

        # Initialize requests
        self.requests = []

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ GET                                                                            │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def get(self):
        """ Performs an HTTP GET request to the page using its pliers' requester """

        # Get URL
        url = self.url

        # Get driver
        driver = self.driver

        # Check if driver is not null
        if driver:

            print("DRIVER")

            # Get URL with driver
            driver.get(url)

            # Iterate over driver requests
            for request in driver.requests:

                # Get response
                response = request.response

                # Initialize request object
                request = Request(url)

                # Set request response
                request.set_response(response)

                # Append request to requests
                self.requests.append(request)

        # Otherwise handle no driver
        else:

            print("REQUESTER")

            # Initialize request object
            request = Request(url)

            # Append request to requests
            self.requests.append(request)

            response = self.requester.get(url)

            # Set request response
            request.set_response(response)
