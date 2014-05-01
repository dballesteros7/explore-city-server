__all__ = ['NotExistentTokenError', 'InvalidTokenError', 'ExpiredTokenError']

class NotExistentTokenError(Exception):
    pass
class InvalidTokenError(Exception):
    pass
class ExpiredTokenError(Exception):
    pass