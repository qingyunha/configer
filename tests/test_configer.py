#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_configer
----------------------------------

Tests for `configer` module.
"""


import os
import unittest

import configer
from configer.configer import \
    ConfigSetError, ConfigUnSupportType


json_example = r"""{
"id": "0001",
"type": "donut",
"name": "Cake",
"ppu": 0.55,
"batters": {
        "batter": [
                { "type": "Regular" },
                { "type": "Chocolate" },
                { "type": "Blueberry" },
                { "type": "Devil's Food" }
            ]
    }
}"""


yaml_example = r"""!!python/unicode 'batters':
  !!python/unicode 'batter':
  - {!!python/unicode 'type': !!python/unicode 'Regular'}
  - {!!python/unicode 'type': !!python/unicode 'Chocolate'}
  - {!!python/unicode 'type': !!python/unicode 'Blueberry'}
  - {!!python/unicode 'type': !!python/unicode 'Devil''s Food'}
!!python/unicode 'id': !!python/unicode '0001'
!!python/unicode 'name': !!python/unicode 'Cake'
!!python/unicode 'ppu': 0.55
!!python/unicode 'type': !!python/unicode 'donut'
"""

C = configer.C


def create_config_file(_type):
    example = eval(_type+"_example")
    filename = "./config." + _type
    with open(filename, 'w') as f:
        f.write(example)


def remove_config_file(_type):
    try:
        os.remove('./config.'+_type)
    except:
        pass


class TestConfiger(unittest.TestCase):

    config_type = 'json'

    @classmethod
    def setUpClass(cls):
        C.reset()
        create_config_file(cls.config_type)
        C.read()

    @classmethod
    def tearDownClass(cls):
        remove_config_file(cls.config_type)

    def test_000_something(self):
        self.assertEqual(C.get("id"), "0001")
        self.assertIsNone(C.get("ids"))
        self.assertIsNotNone(C.get("batters"))
        self.assertIsNotNone(C.get("batters.batter"))

    def test_001_something(self):
        self.assertEqual(C.get("foo"), None)
        C.set_default("foo", 123)
        self.assertEqual(C.get("foo"), 123)
        C.set("foo", 345)
        self.assertEqual(C.get("foo"), 345)
        self.assertEqual(C.get("id"), "0001")
        C.set("id", "0002")
        self.assertEqual(C.get("id"), "0002")

    def test_002_something(self):
        C.set("host.address", "127.0.0.1")
        C.set("host.port", "80")
        self.assertEqual(C.get("host.address"), "127.0.0.1")
        self.assertEqual(C.get("host.port"), "80")

    def test_003_something(self):
        with self.assertRaises(ConfigSetError):
            C.set("host.port.no", "no")

    def test_004_something(self):
        C.set_type('ini')
        with self.assertRaises(ConfigUnSupportType):
            C.read()
        C.type = None

    def test_004_something(self):
        C.set_type('ini')
        with self.assertRaises(ConfigUnSupportType):
            C.read()
        C.type = None

    def test_005_something(self):
        C.bind_env('PATH')
        self.assertIsNotNone(C.get('PATH'))
        os.environ['name'] = 'taoqy'
        self.assertEqual(C.get('name'), 'Cake')
        C.bind_env('name')
        self.assertEqual(C.get('name'), 'taoqy')
        os.environ.pop('name')

    def test_006_something(self):
        C.set_env_prefix("CONFIGER_")
        C.bind_env('PATH')
        self.assertIsNone(C.get('PATH'))
        path = os.getenv('PATH')
        os.environ['CONFIGER_PATH'] = path
        self.assertEqual(C.get('PATH'), path)
        os.environ.pop('CONFIGER_PATH')


class TestConfigerYaml(TestConfiger):
    config_type = 'yaml'



if __name__ == '__main__':
    unittest.main()
