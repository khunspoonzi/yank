# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ TARGET                                                                             │
# └────────────────────────────────────────────────────────────────────────────────────┘


class Target:
    """ A utility class used to represent a target web page or API endpoint """

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CLASS ATTRIBUTES                                                               │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # Initialize response to None
    response = None

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ INIT METHOD                                                                    │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def __init__(self, url, pliers):
        """ Init Method """

        # Set URL
        self.url = url

        # Set pliers
        self.pliers = pliers

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ GET                                                                            │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def get(self):
        """ Performs an HTTP GET request to the page using its pliers' requester """

        # Get response
        response = self.pliers.requester.get(self.url)

        # Set response
        self.response = response

        # Return response
        return response
