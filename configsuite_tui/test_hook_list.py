from configsuite import types
from configsuite import MetaKeys as MK
import configsuite_tui


@configsuite_tui.hookimpl
def configsuite_tui_schema():
    name = "List"
    schema = {
        MK.Type: types.List,
        MK.Content: {
            MK.Item: {
                MK.Type: types.Integer,
                MK.Description: "Integer",
            },
        },
    }

    return {name: schema}
