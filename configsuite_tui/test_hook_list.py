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
                MK.Type: types.NamedDict,
                MK.Content: {
                    "name": {MK.Type: types.String, MK.Description: "Name as a string"},
                    "hobby": {
                        MK.Type: types.String,
                        MK.Description: "Hobby as a string",
                    },
                    "age": {
                        MK.Type: types.Integer,
                        MK.Description: "Age as a positive integer",
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
            },
        },
    }

    return {name: schema}
