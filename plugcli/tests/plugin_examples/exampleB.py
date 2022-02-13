import click
import plugcli

@click.command("exampleB")
def exampleB():  # -no-cov-
    pass

PLUGIN = plugcli.plugin_management.CommandPlugin(
    command=exampleB,
    section="Miscellaneous",
    requires_lib=(1, 0, 0),
    requires_cli=(2, 0, 0),
)
