from google.appengine.ext import testbed

import webtest

from entry_point import app

class TestHarness(object):

    def setup(self):
        self.testbed = testbed.Testbed()
        self.testbed.setup_env(app_id = "_")
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_urlfetch_stub()
        self.testbed.init_blobstore_stub()
        self.testbed.init_files_stub()

    def destroy(self):
        self.testbed.deactivate()

class TestHarnessWithWeb(TestHarness):

    def setup(self):
        self.testapp = webtest.TestApp(app)
        super(TestHarnessWithWeb, self).setup()
