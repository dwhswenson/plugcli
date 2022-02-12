import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from plugcli.cli import *

from plugcli.plugin_management import CommandPlugin

class FakeCLI(CLI):
    COMMAND_SECTIONS = ["Simulation", "Analysis", "Miscellaneous"]
    def get_installed_plugins(self):
        def make_mock(name, helpless=False, return_val=None):
            if return_val is None:
                return_val = name
            mock = MagicMock(return_value=return_val)
            mock.name = name
            if helpless:
                mock.short_help = None
            else:
                mock.short_help = name + " help"
            return mock

        foo_plugin = CommandPlugin(
            command=make_mock('foo'),
            section="Simulation",
            requires_lib=(1, 0, 0),
            requires_cli=(2, 0, 0),
        )
        foo_plugin.attach_metadata(location="foo.py",
                                   plugin_type='file')
        foobar_plugin = CommandPlugin(
            command=make_mock('foo-bar', helpless=True,
                              return_val='foobar'),
            section="Miscellaneous",
            requires_lib=(1, 0, 0),
            requires_cli=(2, 0, 0),
        )
        foobar_plugin.attach_metadata(location='foo_bar.py',
                                      plugin_type='file')
        self.plugin_dict = {
            'foo': foo_plugin,
            'foo-bar': foobar_plugin,
        }
        return [foo_plugin, foobar_plugin]


class TestCLI(object):
    def setup(self):
        self.cli = FakeCLI()
        self.plugin_dict = self.cli.plugin_dict
        self.plugins = list(self.cli.plugin_dict.values())
        # need to copy the plugins since we're changing the list
        for plugin in self.cli.plugins[:]:
            self.cli._deregister_plugin(plugin)

        for plugin in self.plugins:
            self.cli._register_plugin(plugin)

    def test_plugins(self):
        assert self.cli.plugins == self.plugins
        assert self.cli._sections['Simulation'] == ['foo']
        assert self.cli._sections['Miscellaneous'] == ['foo-bar']

    @pytest.mark.parametrize('name', ['foo', 'foo-bar'])
    def test_plugin_for_command(self, name):
        assert self.cli.plugin_for_command(name) == self.plugin_dict[name]

    def test_list_commands(self):
        assert self.cli.list_commands(ctx=None) == ['foo', 'foo-bar']

    @pytest.mark.parametrize('command', ['foo-bar', 'foo_bar'])
    def test_get_command(self, command):
        # this tests that renamings work
        cmd = self.cli.get_command(ctx=None, name=command)
        assert cmd() == 'foobar'

    def test_format_commands(self):
        class MockFormatter(object):
            def __init__(self):
                self.title = None
                self.contents = {}

            def section(self, title):
                self.title = title
                return MagicMock()

            def write_dl(self, rows):
                self.contents[self.title] = rows

        formatter = MockFormatter()
        # add a non-existent command; tests when get_command is None
        self.cli._sections['Workflow'] = ['baz']
        self.cli.format_commands(ctx=None, formatter=formatter)
        foo_row = ('foo', 'foo help')
        foobar_row = ('foo-bar', '')
        assert formatter.contents['Simulation Commands'] == [foo_row]
        assert formatter.contents['Miscellaneous Commands'] == [foobar_row]
        assert len(formatter.contents) == 2
