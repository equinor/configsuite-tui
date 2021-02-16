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
        MK.Type: types.NamedDict,
        MK.Content: {
            "car": {MK.Type: types.String},
            "manufacturer": {MK.Type: types.String},
            "last_serviced": {MK.Type: types.Date},
            "eu_approved": {MK.Type: types.Bool},
            "Additional": {MK.Type: Test_Type},
        },
    }
    return {name: schema}
