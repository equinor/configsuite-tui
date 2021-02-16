import datetime
import curses
import os
import tempfile
import shutil
from unittest import TestCase
import unittest.mock as mock
import npyscreen
import pluggy
from configsuite_tui.tui import tui
from configsuite_tui.config_tools import save
from configsuite_tui import hookspecs
from .schemas import test_schema_2


class Test_Tui_With_Files(TestCase):
    def setUp(self):
        # Create temporary directory
        self.tmpdir = tempfile.mkdtemp()
        os.chdir(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_tui_input_save_return_validate(self):
        with tempfile.NamedTemporaryFile(dir=self.tmpdir) as tmpfile:
            testinput = [
                curses.KEY_DOWN,
                "Jane Doe",
                curses.KEY_DOWN,
                "Electrician",
                curses.KEY_DOWN,
                "35",
                curses.KEY_DOWN,
                curses.ascii.NL,
                curses.KEY_DOWN,
                curses.ascii.NL,
                curses.KEY_DOWN,
                "45.35",
                curses.KEY_DOWN,
                "1999-01-01",
                curses.KEY_DOWN,
                "2011-11-04T00:05:23",
                curses.KEY_UP,
                curses.KEY_UP,
                curses.KEY_UP,
                curses.KEY_UP,
                curses.KEY_UP,
                curses.KEY_UP,
                curses.KEY_UP,
                "^S",
                curses.ascii.NL,
                curses.KEY_RIGHT,
                curses.ascii.NL,
                curses.ascii.NL,
                curses.KEY_DOWN,
                curses.KEY_DOWN,
                curses.ascii.NL,
                "^Q",
            ]
            npyscreen.TEST_SETTINGS["TEST_INPUT"] = testinput
            config, valid = tui(test=True)

            self.assertEqual(
                config,
                {
                    "name": "Jane Doe",
                    "hobby": "Electrician",
                    "age": 35,
                    "active": True,
                    "score": 45.35,
                    "birthday": datetime.date(1999, 1, 1),
                    "last_seen": datetime.datetime(2011, 11, 4, 0, 5, 23),
                },
            )
            self.assertTrue(valid)
            test_string = (
                "name: Jane Doe\nhobby: Electrician\nage: 35\nactive: true\nscore: "
                + "45.35\nbirthday: 1999-01-01\nlast_seen: 2011-11-04 00:05:23\n"
            )
            self.assertEqual(
                tmpfile.read(),
                test_string.encode("utf_8"),
            )

    def test_tui_load_return_validate(self):
        config = {
            "name": "John Doe",
            "hobby": "Carpenter",
            "age": 45,
            "active": True,
            "score": 23.54,
            "birthday": datetime.date(1999, 2, 2),
            "last_seen": datetime.datetime(2011, 12, 4, 0, 4, 15),
        }
        with tempfile.NamedTemporaryFile(dir=self.tmpdir) as tmpfile:
            save(config, tmpfile.name)
            testinput = [
                "^L",
                curses.ascii.NL,
                curses.KEY_RIGHT,
                curses.ascii.NL,
                curses.ascii.NL,
                curses.KEY_DOWN,
                curses.KEY_DOWN,
                curses.ascii.NL,
                "^Q",
            ]
            npyscreen.TEST_SETTINGS["TEST_INPUT"] = testinput
            config, valid = tui(test=True)

            self.assertEqual(
                config,
                {
                    "name": "John Doe",
                    "hobby": "Carpenter",
                    "age": 45,
                    "active": True,
                    "score": 23.54,
                    "birthday": datetime.date(1999, 2, 2),
                    "last_seen": datetime.datetime(2011, 12, 4, 0, 4, 15),
                },
            )
            self.assertTrue(valid)

    def test_cancel_forms_and_no_fork(self):
        testinput = [
            "^A",
            curses.KEY_DOWN,
            curses.ascii.NL,
            "^S",
            curses.KEY_DOWN,
            curses.ascii.NL,
            "^L",
            curses.KEY_DOWN,
            curses.ascii.NL,
            curses.KEY_DOWN,
            curses.KEY_UP,
            "^Q",
        ]
        npyscreen.TEST_SETTINGS["TEST_INPUT"] = testinput
        config, valid = tui()

        self.assertEqual(config, {})
        self.assertFalse(valid)

    def test_load_schema_view_description(self):
        testinput = [
            "^A",
            curses.ascii.NL,
            curses.ascii.NL,
            curses.KEY_DOWN,
            curses.KEY_DOWN,
            curses.ascii.NL,
            "^D",
            curses.ascii.NL,
            curses.ascii.NL,
            curses.KEY_UP,
            "^Q",
        ]
        npyscreen.TEST_SETTINGS["TEST_INPUT"] = testinput
        config, valid = tui(test=True)

        self.assertEqual(
            config,
            {
                "name": "",
                "hobby": "",
                "age": "",
                "active": None,
                "score": "",
                "birthday": None,
                "last_seen": None,
            },
        )
        self.assertFalse(valid)


class Test_Tui_With_Mocked_Schema(TestCase):
    pm = pluggy.PluginManager("configsuite_tui")
    pm.add_hookspecs(hookspecs)
    pm.load_setuptools_entrypoints("configsuite_tui")
    pm.register(test_schema_2)

    @mock.patch("configsuite_tui.tui.get_plugin_manager", return_value=pm)
    def test_load_second_schema(self, mocked_pm):

        testinput = [
            curses.ascii.NL,
            curses.ascii.NL,
            "^Q",
        ]
        npyscreen.TEST_SETTINGS["TEST_INPUT"] = testinput
        config, valid = tui(test=True)

        self.assertEqual(
            config,
            {
                "car": "",
                "manufacturer": "",
                "last_serviced": None,
                "eu_approved": None,
                "Additional": "",
            },
        )
        self.assertFalse(valid)

    @mock.patch("configsuite_tui.tui.get_plugin_manager", return_value=pm)
    def test_fill_second_schema(self, mocked_pm):
        testinput = [
            curses.ascii.NL,
            curses.ascii.NL,
            curses.KEY_DOWN,
            "Porsche 911",
            curses.KEY_DOWN,
            "Porsche",
            curses.KEY_DOWN,
            "2021-01-15",
            curses.KEY_DOWN,
            curses.ascii.NL,
            curses.KEY_DOWN,
            curses.ascii.NL,
            curses.KEY_DOWN,
            "Something",
            curses.KEY_UP,
            curses.KEY_UP,
            curses.KEY_UP,
            curses.KEY_UP,
            curses.KEY_UP,
            "^Q",
        ]
        npyscreen.TEST_SETTINGS["TEST_INPUT"] = testinput
        config, valid = tui(test=True)

        self.assertEqual(
            config,
            {
                "car": "Porsche 911",
                "manufacturer": "Porsche",
                "last_serviced": datetime.date(2021, 1, 15),
                "eu_approved": True,
                "Additional": "Something",
            },
        )
        self.assertTrue(valid)

    @mock.patch("configsuite_tui.tui.get_plugin_manager", return_value=pm)
    def test_error_blocks_quit(self, mocked_pm):
        testinput = [
            "^Q",
        ]
        npyscreen.TEST_SETTINGS["TEST_INPUT"] = testinput

        with self.assertRaises(npyscreen.wgwidget.ExhaustedTestInput):
            tui(test=True)
