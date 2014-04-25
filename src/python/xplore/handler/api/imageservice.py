'''
Module that provides functionality to upload images to the server.

Created on Jan 12, 2014

@author: diegob
'''
from google.appengine.api.images import get_serving_url
from google.appengine.ext.blobstore import create_upload_url
from google.appengine.ext.webapp import blobstore_handlers
import json

from xplore.handler.auth import login_required
from xplore.handler.base import BaseHandler


class ImageUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    '''
    Simple upload handler that stores the given file in the blobstore
    and returns the blobkey to the user, who is responsible of passing
    it to the correct REST resource.
    '''

    def post(self):
        '''
        POST verb that is called after a successful upload to the blobstore,
        the blob key for the newly uploaded image is expected in the image
        field. This key is returned to the user so it can be used in
        a metadata upload in the API.
        '''
        uploaded_images = self.get_uploads('image')
        if len(uploaded_images) > 0:
            # TODO: Weird, react somehow
            pass
        blob_info = uploaded_images[0]
        self.response.headers['Content-Type'] = 'application/json'
        response_results = {'image_key' : str(blob_info.key()),
                            'image_url' : get_serving_url(blob_info)}
        self.response.out.write(json.dumps(response_results))

class ImageUploadUrlProvider(BaseHandler):
    '''
    Request handler that provides an URL for authorized users that can be
    used to upload images to the server.
    '''

    @login_required(redirect = False)
    def get(self):
        '''
        Provide a blobstore upload URL that can be used to upload images
        to the server. Make sure that only authorized user and apps can
        get access to such URLs.
        '''
        upload_url = create_upload_url(self.uri_for('image-upload'))
        self.response.headers['Content-Type'] = 'application/json'
        response_results = {'upload_url' : upload_url}
        self.response.out.write(json.dumps(response_results))
