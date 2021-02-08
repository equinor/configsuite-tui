import pluggy

hookspec = pluggy.HookspecMarker("configsuite_tui")


@hookspec
def configsuite_tui_schema():
    """Register ConfigSuite Schema on ConfigSuite-TUI
    Return dict: {"name": name, "schema": schema}
    name = string
    schema = ConfigSuite schema object
    """
