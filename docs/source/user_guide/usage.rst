Usage
=====
Launching the TUI
-----------------
The TUI can be launched from the CLI, the Python Shell, or inline in a function.

Launching from the CLI
^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: RST

    usage: configsuite_tui [-h] [config] [-s SCHEMA]

**Positional Arguments**

config - Path to the configuration file (Optional)

A configuration file can be provided for the TUI to load on startup.
A schema has to be specified if a configuration is provided, unless the configuration 
file has the schema name annotated at the top of the file.

**Named Arguments**

-s, --schema - Name of schema (Optional)

A schema can be provided to load chosen schema on startup. 
The schema has to be already registered with the TUI.

Launching from Python
^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python

    from configsuite_tui.tui import tui
    tui()

When using the TUI within Python, it can also return the configuration and validation boolean upon exit.

.. code-block:: python

    from configsuite_tui.tui import tui
    config, valid = tui()

Keybindings
-----------
The TUI is operated using the keyboard and a set of keybindings, as will be informed in the TUI.
The keybindings are as follows:

-   :code:`Ctrl+A` - Load Schema
-   :code:`Ctrl+S` - Save Config
-   :code:`Ctrl+L` - Load Config
-   :code:`Ctrl+D` - Show Description (of marked field)
-   :code:`Ctrl+E` - Edit List/Dict (only inside a List or Dict)
-   :code:`Ctrl+Q` - Quit

Schema
------
Config Suite TUI needs a `Config Suite <https://github.com/equinor/configsuite>`_ schema to work.
A schema can be loaded either by specifying it at the CLI, or loading it from the menu using the keybind :code:`Ctrl+A`.

All schemas for use with the TUI has to be registered with the schema plugin system of the TUI.
This has to be done by the developer of the software in which the schema originates.
How to register a schema with the TUI can be seen :ref:`here<Registering a schema>`.

Configuration file
------------------
Config Suite TUI uses PyYAML `PyYAML <https://pyyaml.org/>`_ to work with configuration files. 
A configuration file can be loaded and saved after a schema has been initialized in the TUI.

Loading a configuration can be done from the menu using the keybind :code:`Ctrl+L`. 

Saving can be done from the menu using the keybind :code:`Ctrl+S`.
Quicksave is enabled if a configuration file has been loaded or saved earlier in the same session. 
This is done by double pressing :code:`Ctrl+S`.

A configuration file saved by Config Suite TUI will have the used schema annotated in the header of the file. 
This makes it possible to load the configuration from the CLI without specifying a schema name.

An example configuration file with an annotated schema can be seen below.


.. code-block:: yaml

    !# configsuite-tui: schema=OwnedCars
    name: Kjell
    owned_cars:
    - type: '911'
      brand: Porsche
      previous_owners:
      - Thomas
      - Bernt

