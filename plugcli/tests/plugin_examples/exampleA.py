import click
import plugcli

@click.command("exampleA")
def exampleA():  # -no-cov-
    pass

PLUGIN = plugcli.plugin_management.CommandPlugin(
    command=exampleA,
    section="Simulation",
    requires_lib=(1, 0, 0),
    requires_cli=(2, 0, 0),
)
