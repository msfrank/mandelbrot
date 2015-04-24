import bootstrap

import unittest
import pathlib
import urllib.parse
import tempfile
import shutil
import cifparser

import mandelbrot.instance

class TestInstance(unittest.TestCase):

    tmp_path = pathlib.Path(tempfile.gettempdir(), 'fixture_TestInstance')

    def setUp(self):
        self.tmp_path.mkdir(parents=True)

    def tearDown(self):
        if self.tmp_path.exists():
            shutil.rmtree(str(self.tmp_path))

    def test_create_instance(self):
        "Creating an instance should succeed"
        path = pathlib.Path(self.tmp_path, 'agent')
        instance = mandelbrot.instance.create_instance(path)
        instance.close()

    def test_create_fails_if_instance_exists(self):
        "Creating an instance should raise Exception if instance exists"
        path = pathlib.Path(self.tmp_path, 'agent')
        instance = mandelbrot.instance.create_instance(path)
        instance.close()
        self.assertRaises(Exception, mandelbrot.instance.create_instance, path)

    def test_open_instance(self):
        "Opening an existing instance should succeed"
        path = pathlib.Path(self.tmp_path, 'agent')
        instance = mandelbrot.instance.create_instance(path)
        instance.close()
        instance = mandelbrot.instance.open_instance(path)
        instance.close()
        
    def test_open_fails_if_instance_not_exists(self):
        "Opening an instance should raise Exception if instance doesn't exist"
        path = pathlib.Path(self.tmp_path, 'agent')
        self.assertRaises(Exception, mandelbrot.instance.open_instance, path)

    def test_get_agent_id(self):
        "Getting the agent id for an instance should return None if it has not been set"
        path = pathlib.Path(self.tmp_path, 'agent')
        instance = mandelbrot.instance.create_instance(path)
        self.assertIsNone(instance.get_agent_id())
        instance.close()

    def test_set_agent_id(self):
        "Setting the agent id for an instance should succeed"
        path = pathlib.Path(self.tmp_path, 'agent')
        instance = mandelbrot.instance.create_instance(path)
        instance.set_agent_id(cifparser.make_path('foo'))
        self.assertEqual(instance.get_agent_id(), cifparser.make_path('foo'))
        instance.close()

    def test_get_endpoint_url(self):
        "Getting the endpoint url for an instance should return None if it has not been set"
        path = pathlib.Path(self.tmp_path, 'agent')
        instance = mandelbrot.instance.create_instance(path)
        self.assertIsNone(instance.get_endpoint_url())
        instance.close()

    def test_set_endpoint_url(self):
        "Setting the endpoint url for an instance should succeed"
        path = pathlib.Path(self.tmp_path, 'agent')
        instance = mandelbrot.instance.create_instance(path)
        instance.set_endpoint_url(urllib.parse.urlparse('http://foo.com'))
        self.assertEqual(urllib.parse.urlunparse(instance.get_endpoint_url()), 'http://foo.com')
        instance.close()
