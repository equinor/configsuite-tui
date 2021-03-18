import unittest
import tempfile
from configsuite import types
from configsuite import MetaKeys as MK
from configsuite_tui.config_tools import load, save, validate


class TestConfig(unittest.TestCase):
    def setUp(self):
        # Test schema
        self.schema = {
            MK.Type: types.NamedDict,
            MK.Content: {
                "name": {MK.Type: types.String},
                "hobby": {MK.Type: types.String},
                "age": {MK.Type: types.Integer},
            },
        }

    def test_saving_loading_and_validating_config(self):
        with tempfile.TemporaryDirectory() as tempdir:
            filepath = tempdir + "/test.yml"
            config = {"name": "Joe Biden", "hobby": "President", "age": 78}
            save(config, filepath, "test")
            loaded_config, loaded_schema = load(filepath)
            self.assertTrue(validate(loaded_config, self.schema, []))
            self.assertEqual(loaded_schema, "test")

    def test_get_errors(self):
        config = {"name": 23, "hobby": True, "age": "76"}
        valid, errors = validate(config, self.schema, [])
        expected_errors = {
            "hobby": "Is x a string is false on input 'True'",
            "age": "Is x an integer is false on input '76'",
            "name": "Is x a string is false on input '23'",
        }
        self.assertFalse(valid)
        self.assertEqual(errors, expected_errors)
