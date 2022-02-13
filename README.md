[![tests](https://github.com/dwhswenson/plugcli/actions/workflows/ci.yml/badge.svg)](https://github.com/dwhswenson/plugcli/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/dwhswenson/plugcli/branch/main/graph/badge.svg?token=Pkbu1poegg)](https://codecov.io/gh/dwhswenson/plugcli)

# plugcli
Simple click-based tools for plugin-based CLIs.

`plugcli` is a small extension of
[`click`](https://click.palletsprojects.com/en/latest/). It provides several
useful pieces of functionality, including:

* A plugin registration system, allowing user-created plugins to be registered
  either by installing in a given namespace or by adding plugin files to a
  specified directory.
* A CLI class that uses that plugin registration system to register new
  subcommands, and which separates subcommands into sections for the `--help`
  documentation.
* Tools to facilitate reuse of parameters between different subcommands,
  helping ensure a consistent user interface. While much of this is already
  enabled by `click`, the tools in `plugcli` are particularly useful in cases
  where `click`'s callbacks may not be sufficient, such as when the order in
  which parameters are parsed is important.


## Installing `plugcli`

`plugcli` can be installed through the standard mechanisms: `pip install
plugcli`; or `conda install -c conda-forge plugcli`, or install from source
using setuptools (`python setup.py install`, etc.) Its only direct dependency
is `click`.

## Plugin registration

The plugin registration system is designed to handle plugins that can
essentially be treated as entries in a dispatch table. That is, these are
plugins that are designed to give optionally-used additional functionality.
Subcommands of the CLI are one example, and `plugcli` provides specific tools
for this use case. Other examples might support for additional keywords when
processing a user input file, or support for other options in menus for
interactive user interfaces.

The basic approach to writing plugins is to wrap user-defined functionality in
some subclass of the `plugcli.Plugin` class, which may also encapsulate
additional metadata of use to the program. For example, the
`plugcli.CommandPlugin` class also takes a `section` label, to tell which help
section the plugin command should be listed in.

A program defines where a user can put plugins by creating one or more
`PluginLoader`s. The two concrete classes of `PluginLoader` are
`FilePluginLoader`, which takes a directory and searches for any plugins in
Python files in that directory, and the `NamespacePluginLoader`, which takes a
string representing a Python namespace and searches for any plugins in
modules/subpackages found in that namespace.

## CLI Class

The `plugcli.CLI` class subclasses `click.CLI`, adding support for loading
commands from the `plugcli` plugin structure, and sorting commands in `--help`
into sections defined by the developer.

Users must subclass `plugcli.CLI`. The subclass should set the class variable
`COMMAND_SECTIONS` to a list of the section names used in sorting plugins for
the help. The subclass should also implement the `get_installed_plugins`
method, which uses a selection of `PluginLoader`s that determine the locations
where plugins will be found and registered.

## Reusable parameters

The goal of `plugcli`'s reusable parameters is to ensure consistency throughout
different subcommands by encapsulating names and behavior of parameters that
can be shared. This is done with the `plugcli.Option` and `plugcli.Argument`
classes, which take the same parameters as the `click.option` and
`click.parameter` decorators, plus a `getter` keyword-only argument that takes
an callable which converts the user input as processed by `click` and returns
an object ready for use in the CLI's underlying library code. This takes a
user-defined `context` dict, which provides more flexibility than the standard
`click` callbacks.

You can create a standard click decorator for one of these parameters with the
`.parameter()` method, allowing a single parameter instance to be reused in
multiple subcommands. `click` arguments set in the initialization of the
`plugcli` parameter can be overridden by keyword arguments passed to the
`.parameter` method, allowing some customizability in special cases (e.g., to
allow the parameter to be called a different number of times) while retaining
most of the consistency.

## History

`plugcli` was originally part of the [OpenPathSampling
CLI](https://github.com/openpathsampling/openpathsampling-cli). It was
refactored into a separate package as it become more evident that it filled a
small, but useful, niche, and could be reused in other projects.
