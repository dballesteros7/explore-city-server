'''
Module that contains several utilities for parsing inputs from HTTP
requests.

Created on Jan 7, 2014

@author: diegob
'''

def parse_float(input_value, l_limit = 0, u_limit = None):
    '''
    Check the input string and parse it as a float,
    constrained to a lower and upper limit. If the value
    is outside those boundaries then snap it to the closest one.
    If the string is invalid then return 0.0.
    '''
    # TODO: Throw a tailored exception instead of passing bad values as good.
    result = 0.0
    try:
        result = float(input_value)
    except:
        pass
    if l_limit is not None and result < l_limit:
        result = l_limit
    if u_limit is not None and result > u_limit:
        result = u_limit
    return result

def parse_int(input_value, l_limit = 0, u_limit = None):
    '''
    Check the input string and parse it as an int, constrained to a lower
    and upper limit. If the values is outside those boundaries then snap it to
    the closest one. If the string is an invalid string then return 0.
    '''
    return int(parse_float(input_value, l_limit, u_limit))

def parse_bool(input_value):
    '''
    Check the input string and parse it as a boolean value. The accepted
    values for True are:
        - True (case-insensitive)
        - 1
        - T or t
    Accepted values for false are:
        - False (case-insensitive)
        - 0
        - F or f
    Any other value will raise an exception.
    '''
    if input_value.strip().lower() in ['true', 't', '1']:
        return True
    if input_value.strip().lower() in ['false', 'f', '0']:
        return False
    return False