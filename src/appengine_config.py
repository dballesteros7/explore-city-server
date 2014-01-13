'''
Module with config overrides for the application

Created on Jan 12, 2014

@author: diegob
'''

import os


def namespace_manager_default_namespace_for_request():
    '''
    Set the namespace according to the current version answering the request.
    The expected namespaces are dev and prod only.
    '''
    major_ver, _ = os.environ.get('CURRENT_VERSION_ID').rsplit('.', 1);
    # For compatibility, set the namespace for version 1 to None
    if major_ver == "1":
        return None
    return major_ver