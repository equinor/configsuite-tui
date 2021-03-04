from configsuite import types
from configsuite import MetaKeys as MK
import configsuite_tui


@configsuite_tui.hookimpl
def configsuite_tui_schema():
    name = "Named Dict"
    schema = {
        MK.Type: types.NamedDict,
        MK.Content: {
            "name": {MK.Type: types.String, MK.Description: "Name as a string"},
            "hobby": {MK.Type: types.String, MK.Description: "Hobby as a string"},
            "age": {
                MK.Type: types.Integer,
                MK.Description: "Age as a positive integer",
            },
            "active": {MK.Type: types.Bool, MK.Description: "Boolean, True or False"},
            "score": {
                MK.Type: types.Number,
                MK.Description: "A number with or without decimals",
            },
            "birthday": {
                MK.Type: types.Date,
                MK.Description: "Birthday as a date on iso format e.g. '1999-02-17'",
            },
            "last_seen": {
                MK.Type: types.DateTime,
            },
            "list_of_dogs": {
                MK.Type: types.List,
                MK.Content: {
                    MK.Item: {
                        MK.Type: types.String,
                        MK.Description: "Name of dog",
                    },
                },
            },
        },
    }

    return {name: schema}
