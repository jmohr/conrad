import os
import signal
import subprocess
import time

from conrad.adapter import Rest
from conrad.test import resource
from conrad.test.units.adapter import GenericAdapter

class TestRestAdapter(GenericAdapter):

    def setup(self):
        self.api_server = subprocess.Popen(resource('rest_test_server.py').name, shell=True)
        time.sleep(5)
        self.adapter = Rest('http://localhost:5000/api')

    def teardown(self):
        os.kill(self.api_server.pid, signal.SIGTERM)
        time.sleep(1)