import configsuite
from configsuite import types
from configsuite import MetaKeys as MK
import configsuite_tui


@configsuite.validator_msg("Is x a string")
def _is_test(x):
    return isinstance(x, str)


Test_Type = configsuite.BasicType("Test_Type", _is_test)


@configsuite_tui.hookimpl
def configsuite_tui_schema():
    name = "test"
    schema = {
        MK.Type: types.List,
        MK.Content: {
            MK.Item: {
                MK.Type: types.List,
                MK.Content: {
                    MK.Item: {
                        MK.Type: types.Integer,
                    },
                },
            },
        },
    }
    return {name: schema}
