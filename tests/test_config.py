import pytest
from configsuite import ConfigSuite, types
from configsuite import MetaKeys as MK
from configsuite_tui.config import load


@pytest.fixture()
def schema():
    s = {
        MK.Type: types.NamedDict,
        MK.Content: {
            "name": {MK.Type: types.String},
            "hobby": {MK.Type: types.String},
            "age": {MK.Type: types.Integer},
        },
    }
    return s


def test_loading_config(schema):
    c = load("tests/data/simple.yml")
    config = ConfigSuite(c, schema, deduce_required=True)
    assert config.valid
