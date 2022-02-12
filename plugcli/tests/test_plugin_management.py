import pytest
from unittest.mock import MagicMock

import pathlib
import importlib

from plugcli.plugin_management import *

# need to check that CLI is assigned to correct type
import click


class PluginLoaderTest(object):
    def setup(self):
        self.expected_section = {'exampleA': "Simulation",
                                 'exampleB': "Miscellaneous"}

    def _make_candidate(self, command):
        raise NotImplementedError()

    @pytest.mark.parametrize('command', ['exampleA', 'exampleB'])
    def test_find_candidates(self, command):
        candidates  = self.loader._find_candidates()
        str_candidates = [str(c) for c in candidates]
        assert str(self._make_candidate(command)) in str_candidates

    @pytest.mark.parametrize('command', ['exampleA', 'exampleB'])
    def test_make_nsdict(self, command):
        candidate = self._make_candidate(command)
        nsdict = self.loader._make_nsdict(candidate)
        plugin = nsdict['PLUGIN']
        assert plugin.section == self.expected_section[command]
        assert isinstance(plugin.command, click.Command)

    @pytest.mark.parametrize('command', ['exampleA', 'exampleB'])
    def test_call(self, command):
        plugins = self.loader()
        plugin_dict = {p.name: p for p in plugins}
        plugin = plugin_dict[command]
        assert plugin.name == command
        assert str(plugin.location) == str(self._make_candidate(command))
        assert isinstance(plugin.command, click.Command)
        assert plugin.section == self.expected_section[command]
        assert plugin.plugin_type == self.plugin_type


class TestFilePluginLoader(PluginLoaderTest):
    def setup(self):
        super().setup()
        # use our own commands dir as a file-based plugin
        parent = pathlib.Path(__file__).resolve().parent
        self.commands_dir = parent / "plugin_examples"
        self.loader = FilePluginLoader(self.commands_dir, CommandPlugin)
        self.plugin_type = 'file'

    def _make_candidate(self, command):
        return self.commands_dir / (command + ".py")


class TestNamespacePluginLoader(PluginLoaderTest):
    def setup(self):
        super().setup()
        self.namespace = "plugcli.tests.plugin_examples"
        self.loader = NamespacePluginLoader(self.namespace, CommandPlugin)
        self.plugin_type = 'namespace'

    def _make_candidate(self, command):
        name = self.namespace + "." + command
        return importlib.import_module(name)
