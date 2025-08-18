"""OpenPathSampling command line interface

This contains the "main" class/functions for running the OPS CLI.
"""
# builds off the example of Group in click's docs
import collections
import os
import pathlib

import click
# import click_completion
# click_completion.init()

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class CLI(click.Group):
    """Main class for the command line interface

    Most of the logic here is about handling the plugin infrastructure.
    """
    def __init__(self, *args, **kwargs):
        # the logic here is all about loading the plugins
        self._get_command = {}
        self._sections = collections.defaultdict(list)
        self.plugins = []

        plugins = self.get_installed_plugins()
        for plugin in plugins:
            self._register_plugin(plugin)

        super().__init__(*args, **kwargs)

    def get_installed_plugins(self):
        raise NotImplementedError()

    @property
    def _command_sections(self):
        try:
            return self.COMMAND_SECTIONS
        except AttributeError:
            raise NotImplementedError("Subclasses must include class "
                                      "variable 'COMMAND_SECTIONS'")

    def _section_label(self, section_name):
        return section_name + " Commands"

    def _register_plugin(self, plugin):
        self.plugins.append(plugin)
        # normalize underscores to hyphens
        name = plugin.name.replace('_', '-')
        self._get_command[name] = plugin.command
        self._sections[plugin.section].append(name)

    def _deregister_plugin(self, plugin):
        # mainly used in testing
        self.plugins.remove(plugin)
        del self._get_command[plugin.name]
        self._sections[plugin.section].remove(plugin.name)

    def plugin_for_command(self, command_name):
        return {p.name: p for p in self.plugins}[command_name]

    def list_commands(self, ctx):
        return list(self._get_command.keys())

    def get_command(self, ctx, name):
        name = name.replace('_', '-')  # allow - or _ from user
        return self._get_command.get(name)

    def _section_sort_commands(self, section, commands):
        """
        Parameters
        ----------
        section : str
        commands : Iterable[str]
        """
        yield from commands

    def format_commands(self, ctx, formatter):
        for sec in self._command_sections:
            cmds = self._sections.get(sec, [])
            rows = []
            for cmd in self._section_sort_commands(sec, cmds):
                command = self.get_command(ctx, cmd)
                if command is None:
                    # TODO: there is test code that claims to cover this,
                    # but it isn't getting covered; investigate why
                    continue
                rows.append((cmd, command.short_help or ''))

            if rows:
                with formatter.section(self._section_label(sec)):
                    formatter.write_dl(rows)
