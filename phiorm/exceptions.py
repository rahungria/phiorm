import philog


class ORMException(Exception):
    pass


class ORMFatal(ORMException):
    def __init__(self, msg):
        self.msg = msg
        philog.fatal(
            f'Exception Caught: {msg}.'
        )

    def __str__(self):
        return self.msg


class ORMError(ORMException):
    def __init__(self, msg):
        self.msg = msg
        philog.error(
            f'Exception Caught: {msg}.'
        )

    def __str__(self):
        return self.msg


class RequiredFieldError(ORMException):
    pass


class ValidationError(ORMException):
    pass


class ModelPermissionError(ORMException):
    pass


class RepeatedPKError(ORMException):
    pass
