'''Module that provides method to verify inputs coming from external sources,
such as web forms or API calls.

This is a collection of functions that provide the following interface:

:param input_value: The input to test.
:type input_value: str, float.
:raises: :class:`LexiconError` If the input value is not valid, this should
         provide some explanation on why the error happened but without
         including the original error for security reasons.

This module also provides base errors.
'''

import re


class LexiconError(Exception):
    '''Base lexicon error.
    
    Attributes:
        msg -- Error message explaining why the input didn't pass validation.
    '''

    def __init__(self, msg):
        self.msg = msg

class IncorrectLengthError(LexiconError):
    '''Lexicon error raised when the input has incorrect length.'''
    def __init__(self):
        LexiconError.__init__(self, msg = 'The input text is of incorrect length.')

class NotMatchingRegularExpression(LexiconError):
    '''Lexicon error that applies to any input that doesn't match the expected
    regular expression.'''
    def __init__(self):
        LexiconError.__init__(self, msg = 'The input text does not match the' +
                              ' expected regular expression.')

_supported_providers = ['google']

def string_input(lexicon_func):
    '''Decorator that ensures that the input is a string, this is to avoid
    choking on non-string inputs when doing matching with the regex engine.
    '''
    def _string_input(input_value):
        return lexicon_func(str(input_value))
    return _string_input

_alphanumeric = re.compile('^[A-Z0-9]+$', re.IGNORECASE)
_email = re.compile('^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$', re.IGNORECASE)

@string_input
def username(input_value):
    '''Username lexicon definition. Usernames are alphanumeric strings with no
    more than 12 characters and no less than 4.
    '''
    if len(input_value) > 12 or len(input_value) < 4:
        raise IncorrectLengthError
    if not _alphanumeric.match(input_value):
        raise NotMatchingRegularExpression()
    return

@string_input
def email(input_value):
    '''Email lexicon definition. E-mails follow the e-mail address format.'''
    if not _email.match(input_value):
        raise NotMatchingRegularExpression()
    return

@string_input
def provider(input_value):
    """Provider lexicon definition. This checks against a pre-defined list of
    accepted provider."""
    for provider in _supported_providers:
        if input_value.lower() == provider:
            break
    else:
        raise NotMatchingRegularExpression()