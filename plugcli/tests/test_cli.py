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

        underscored_plugin = CommandPlugin(
            command=make_mock("baz_qux", helpless=True,
                              return_val="baz_qux"),
            section="Miscellaneous",
            requires_lib=(1, 0, 0),
            requires_cli=(2, 0, 0),
        )
        self.plugin_dict = {
            'foo': foo_plugin,
            'foo-bar': foobar_plugin,
            'baz-qux': underscored_plugin,
        }
        return [foo_plugin, foobar_plugin]

class MockFormatter(object):
    def __init__(self):
        self.title = None
        self.contents = {}

    def section(self, title):
        self.title = title
        return MagicMock()

    def write_dl(self, rows):
        self.contents[self.title] = rows


class FakeCLIResorted(FakeCLI):
    def _section_sort_commands(self, section, commands):
        # default is foo-bar then baz-qux, this should flip the order
        yield from sorted(commands)


class TestCLI(object):
    def setup_method(self):
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
        assert self.cli._sections['Miscellaneous'] == ['foo-bar', 'baz-qux']

    @pytest.mark.parametrize('name', ['foo', 'foo-bar'])
    def test_plugin_for_command(self, name):
        assert self.cli.plugin_for_command(name) == self.plugin_dict[name]

    def test_list_commands(self):
        expected = list(self.plugin_dict)
        assert self.cli.list_commands(ctx=None) == expected

    @pytest.mark.parametrize('command, output', [
        ('foo-bar', 'foobar'),
        ('foo_bar', 'foobar'),
        ('baz-qux', 'baz_qux'),
        ('baz_qux', 'baz_qux'),
    ])
    def test_get_command(self, command, output):
        # this tests that renamings work
        cmd = self.cli.get_command(ctx=None, name=command)
        assert cmd() == output

    def test_format_commands(self):
        formatter = MockFormatter()
        # add a non-existent command; tests when get_command is None
        self.cli._sections['Workflow'] = ['baz']
        self.cli.format_commands(ctx=None, formatter=formatter)
        foo_row = ('foo', 'foo help')
        foobar_row = ('foo-bar', '')
        bazqux_row = ('baz-qux', '')
        assert formatter.contents['Simulation Commands'] == [foo_row]
        assert formatter.contents['Miscellaneous Commands'] == [foobar_row,
                                                                bazqux_row]
        assert len(formatter.contents) == 2

    def test_section_sort_commands(self):
        cli = FakeCLIResorted()
        # deal with the fact that baz-qux isn't registered
        plugins = list(cli.plugin_dict.values())
        assert len(plugins) == 3
        for plugin in cli.plugins[:]:
            cli._deregister_plugin(plugin)

        for plugin in plugins:
            cli._register_plugin(plugin)

        assert len(cli.plugins) == 3

        formatter = MockFormatter()
        cli.format_commands(ctx=None, formatter=formatter)
        foo_row = ('foo', 'foo help')
        foobar_row = ('foo-bar', '')
        bazqux_row = ('baz-qux', '')
        assert formatter.contents['Simulation Commands'] == [foo_row]
        assert formatter.contents['Miscellaneous Commands'] == [bazqux_row,
                                                                foobar_row]


def test_abstract_no_command_section():
    # If COMMAND_SECTIONS is not defined, format_commands raises
    # NotImplementedError
    class MyCLI(CLI):
        def get_installed_plugins(self):
            return []

    cli = MyCLI()
    with pytest.raises(NotImplementedError):
        cli.format_commands(ctx=None, formatter=None)
