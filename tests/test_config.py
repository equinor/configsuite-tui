import pytest
from configsuite import types
from configsuite import MetaKeys as MK
from configsuite_tui.config import load, save, validate


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


def test_saving_loading_and_validating_config(tmpdir, schema):
    config = {"name": "Joe Biden", "hobby": "President", "age": 78}
    save(config, tmpdir.join("test.yml"))
    loaded_config = load(tmpdir.join("test.yml"))
    assert validate(loaded_config, schema)
