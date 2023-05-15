class AuthenticationException(Exception):
    """Raised when authentication fails for a service.

    Attributes:
        service: The name of the service we attempted to authenticate to.
        message: A message describing the error
    """

    def __init__(self, service, exception, location):
        self.service = service
        x = str(location)
        super().__init__(
            f"Failed to authenticate to {self.service} services.\nUnderlying error was: {str(exception)} in {x}"
        )
