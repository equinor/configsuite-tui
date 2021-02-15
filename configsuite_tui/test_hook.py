from configsuite import types
from configsuite import MetaKeys as MK
import configsuite_tui


@configsuite_tui.hookimpl
def configsuite_tui_schema():
    name = "test"
    schema = {
        MK.Type: types.NamedDict,
        MK.Content: {
            "name": {MK.Type: types.String},
            "hobby": {MK.Type: types.String},
            "age": {MK.Type: types.Integer},
            "active": {MK.Type: types.Bool},
            "score": {MK.Type: types.Number},
            "birthday": {MK.Type: types.Date},
        },
    }

    return {name: schema}
