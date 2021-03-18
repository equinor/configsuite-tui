from configsuite import types
from configsuite import MetaKeys as MK
import configsuite_tui


@configsuite_tui.hookimpl
def configsuite_tui_schema():
    name = "test"
    schema = {
        MK.Type: types.NamedDict,
        MK.Content: {
            "name": {MK.Type: types.String, MK.Description: "Name as a string"},
            "owned_cars": {
                MK.Type: types.List,
                MK.Content: {
                    MK.Item: {
                        MK.Type: types.NamedDict,
                        MK.Content: {
                            "type": {MK.Type: types.String, MK.Description: "Car Type"},
                            "brand": {
                                MK.Type: types.String,
                                MK.Description: "Car Brand",
                            },
                            "previous_owners": {
                                MK.Type: types.List,
                                MK.Content: {
                                    MK.Item: {
                                        MK.Type: types.String,
                                        MK.Description: "Name of previous owners",
                                    },
                                },
                            },
                            "random_info": {
                                MK.Type: types.Dict,
                                MK.Content: {
                                    MK.Key: {MK.Type: types.String},
                                    MK.Value: {MK.Type: types.String},
                                },
                            },
                        },
                    },
                },
            },
        },
    }
    return {name: schema}
