'''Module that defines tools to ensure authentication when requesting
methods to the server.

.. moduleauthor:: Diego Ballesteros <diegob@student.ethz.ch>
'''


def login_required(redirect = True, admin_only = False):
    '''Function decorator that allows the use of optional parameters
    when using the class decorator.
    Note that this decorator must always be called in the definition even
    if the default parameters are not overwritten, i.e.
    ::

        @login_redirect()
        def get(self):
            pass

    Instead of:
    ::

        @login_redirect
        def get(self):
            pass
    '''
    def _login_required(func):
        '''Wrapper function that accepts the unbounded function and creates
        the descriptor with the optional parameters set in the closure.
        '''
        return LoginRequired(func, redirect, admin_only)
    return _login_required

class LoginRequired(object):
    '''Descriptor class that implements the checks for login based on a session
    cookies before providing access to the given handler functions.
    '''

    def __init__(self, func, redirect, admin_only):
        '''Initialize the decorator, setting the redirect attribute to indicate
        if the decorator should redirect when the user is logged in, or instead
        abort the operation. This second option is preferred for API calls
        which are not made by users directly but instead applications. It also
        allows a admin_only parameter that indicates whether admin status
        should be checked.
        The first argument of this method is the unbound handler function
        definition that it decorates.
        '''
        self._func = func
        self._redirect = redirect
        self._check_admin = admin_only
        self._instance = None

    def __get__(self, obj, owner):
        '''Get method that is called to retrieve the bound function to call
        when a call is made to the decorated handler method. It stores
        the instance of the handler and returns a bound __call_ function.
        '''
        self._instance = obj
        return self.__call__

    def __call__(self, *args, **kwargs):
        '''Call that checks that an user is logged in before executing the
        given handler method. It checks the session cookie for this, an user
        is logged in when the '_user_logged_in' flag is present and set to True.
        This call must be bound to an instance of the login_required descriptor
        that contains a valid _instance object that refers to the handler
        instance that invoked the decorated method.
        '''
        # TODO: Verify cookie/session expiration.
        if self._instance.session.get('_user_logged_in', None) and \
            (not self._check_admin or self._instance.session.get('_admin_user', None)):
                return self._func(self._instance, *args, **kwargs)
        else:
            if self._redirect:
                redirect_target = self._instance.uri_for('login-page', 
                                        redirect = self._instance.request.url)
                self._instance.redirect(redirect_target, 
                                        abort = True)
            else:
                self._instance.abort(401)

def login_user(user_instance, session):
    '''Function that provides the ability to log in an user given an instance of
    :class:`models.User` which represents the user in the datastore.

    :param user_instance: User instance in the datastore.
    :type user_instance: :class:`models.User`
    :param session: Session instance to record the log in.
    '''
    session['_user_logged_in'] = True
    session['_user_id'] = user_instance.key.urlsafe()
    if user_instance.admin_status:
        session['_admin_user'] = True

def logout_user(session):
    '''Function that provides the ability to log out the current user by
    removing the corresponding records from the given session object.
    
    :param session: Session instance where the log in is recorded.
    '''
    if 'user_logged_in' in session:
        del session['user_logged_in']
        del session['_user_id']
    if '_admin_user' in session:
        del session['_admin_user']
