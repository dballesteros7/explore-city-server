from handler.base import BaseHandler
import secrets


class TourerPage(BaseHandler):
    """
    """

    def get(self):
        """
        """
        context = {'google_maps_key' : secrets.GOOGLE_APP_BROWSER_KEY}
        self.render_response('tourer.html', **context)
