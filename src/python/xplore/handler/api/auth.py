import calendar
import json

from xplore.database.models import User, AccessToken
from xplore.database.models.user import NonExistentUserError
from xplore.handler.api.base_service import BaseResource


class TokenResource(BaseResource):
    """Resource class that handles the creation and invalidation of session
    tokens granted to the mobile app.
    """

    def get(self):
        """Retrieve a limited-life token for the given user, the required input
        is the username for identification and a JSON web token provided
        by the Google Auth API for security purposes.

        This invalidates any existing tokens in the datastore first, before
        issuing a new one.
        """
        # TODO: IMPLEMENT VALIDATION OF JSON WEB TOKEN FROM APP
        parameters = self.parse_request_body()
        the_user = User.get_by_username(parameters['username'])
        if the_user is None:
            raise NonExistentUserError(parameters['username'])
        AccessToken.invalidate_tokens(the_user)
        token = AccessToken.create(the_user)
        self.build_base_response()
        response_body = {'access_token' : token.token_string,
                         'expires_on' : calendar.timegm(token.expires_on.utctimetuple()),
                         'created_on' : calendar.timegm(token.created_on.utctimetuple()) }
        self.response.out.write(json.dumps(response_body))
