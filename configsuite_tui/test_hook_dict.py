from configsuite import types
from configsuite import MetaKeys as MK
import configsuite_tui


@configsuite_tui.hookimpl
def configsuite_tui_schema():
    name = "Dict"
    schema = {
        MK.Type: types.Dict,
        MK.Content: {
            MK.Key: {MK.Type: types.String},
            MK.Value: {MK.Type: types.Integer},
        },
    }

    return {name: schema}
