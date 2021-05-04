Schema Plugin
=============
Config Suite TUI has a plugin system powered by `pluggy <https://pluggy.readthedocs.io/en/latest/>`_.
This means that any Python module can register its schemas for use with Config Suite TUI. 
All registered schemas will automatically appear in Config Suite TUI.

Registering a schema
--------------------
A pluggy hook implementation has to be filled to register a schema with Config Suite TUI.
The hook specification for the TUI is simple and is defined as follows:

.. code-block:: python

    import pluggy

    hookspec = pluggy.HookspecMarker("configsuite_tui")

    @hookspec
    def configsuite_tui_schema():
        """Register Config Suite schema in Config Suite TUI
        Return dict: {name: schema}
        name = string
        schema = Config Suite schema object
        """

An example of a hook implementation can look like this:

.. code-block:: python

    # configsuite_tui_plugin.py
    import configsuite_tui
    from configsuite import types
    from configsuite import MetaKeys as MK


    @configsuite_tui.hookimpl
    def configsuite_tui_schema():
        name = "Plugin_test"
        schema = {
            MK.Type: types.NamedDict,
            MK.Content: {
                "name": {MK.Type: types.String},
                "hobby": {MK.Type: types.String},
                "age": {MK.Type: types.Integer},
            },
        }

        return {name: schema}

The hook implementation will then have to be registered upon installation using `setuptools <https://pypi.org/project/setuptools/>`_.
This is done by adding an entry point for Config Suite TUI into the software's :code:`setup.py` file. 
An example of this can be seen below:

.. code-block:: python

    from setuptools import setup

    setup(
        name="module-name",
        install_requires="configsuite_tui",
        entry_points={"configsuite_tui": ["plugin = configsuite_tui_plugin"]},
        py_modules=["configsuite_tui_plugin"],
    )

More in depth information about using the plugin system can be found in the `pluggy documentation <https://pluggy.readthedocs.io/en/latest/>`_.