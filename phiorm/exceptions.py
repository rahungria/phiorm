class ORMException(Exception):
    pass


class RequiredFieldError(ORMException):
    pass


class ValidationError(ORMException):
    pass


class ModelPermissionError(ORMException):
    pass


class RepeatedPKError(ORMException):
    pass
