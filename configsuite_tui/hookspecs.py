import pluggy

hookspec = pluggy.HookspecMarker("configsuite_tui")


@hookspec
def configsuite_tui_schema():
    """Register Config Suite schema in Config Suite TUI
    Return dict: {name: schema}
    name = string
    schema = Config Suite schema object
    """
