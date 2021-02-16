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
            save(config, filepath)
            loaded_config = load(filepath)
            self.assertTrue(validate(loaded_config, self.schema))
