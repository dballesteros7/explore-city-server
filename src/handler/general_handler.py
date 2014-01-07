'''
Module with general handlers that serve some of the application's
server URIs.

Created on Dec 13, 2013

@author: diegob
'''

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
import urllib


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    '''
    This handler provides an image from the blobstore given its
    key in the resource. E.g. /serve/<blob-store-key-string>
    '''
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)
