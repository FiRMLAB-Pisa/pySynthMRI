class NotLoadedMapError(Exception):
    """Exception raised when a request image is not yet loaded or synthesized
    Parameters:
        message: explanation of the error
    """

    def __init__(self, message="Requested image not exists"):
        self.message = message
        super().__init__(self.message)


class NotSelectedMapError(Exception):
    """Exception raised when a synthetic image is not created and user try to interact with it
    Parameters:
        message: explanation of the error
    """

    def __init__(self, message="Synthetic map not generated"):
        self.message = message
        super().__init__(self.message)
