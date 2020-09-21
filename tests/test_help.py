# Copyright 2020 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For further info, check https://github.com/canonical/charmcraft

import textwrap
from unittest.mock import patch

import pytest

from charmcraft.main import COMMAND_GROUPS

from charmcraft.helptexts import (
    get_command_help,
    get_detailed_help,
    get_usage_message,
    get_full_help,
)
from tests.factory import create_command


# -- verifications on different short help texts

all_commands = list.__add__(*[commands for _, _, commands in COMMAND_GROUPS])


@pytest.mark.parametrize('command', all_commands)
def test_aesthetic_help_msg(command):
    """All the real commands help msg start with uppercase and ends with a dot."""
    msg = command.help_msg
    assert msg[0].isupper() and msg[-1] == '.'


@pytest.mark.parametrize('command', all_commands)
def test_aesthetic_args_options_msg(command):
    """All the real commands args/options help messages start with uppercase and end with a dot."""
    class FakeParser:
        """A fake to get the arguments added."""

        def add_argument(self, *args, **kwargs):
            help_msg = kwargs.get('help')
            assert help_msg, "The help message must be present in each option"
            assert help_msg[0].isupper() and help_msg[-1] == '.'

    command('group').fill_parser(FakeParser())


def test_get_usage_message():
    """Check the general "usage" text."""
    text = get_usage_message('charmcraft build', 'bad parameter for the build')
    expected = textwrap.dedent("""\
        Usage: charmcraft [OPTIONS] COMMAND [ARGS]...
        Try 'charmcraft build -h' for help.

        Error: bad parameter for the build
    """)
    assert text == expected


# -- bulding of the big help text outputs

def test_default_help_text():
    """All different parts for the default help."""
    cmd1 = create_command('cmd1', 'Cmd help which is very long but whatever.', common_=True)
    cmd2 = create_command('command-2', 'Cmd help.', common_=True)
    cmd3 = create_command('cmd3', 'Extremely ' + 'super crazy long ' * 5 + ' help.', common_=True)
    cmd4 = create_command('cmd4', 'Some help.')
    cmd5 = create_command('cmd5', 'More help.')
    cmd6 = create_command('cmd6-really-long', 'More help.', common_=True)
    cmd7 = create_command('cmd7', 'More help.')

    command_groups = [
        ('group1', 'help text for g1', [cmd6, cmd2]),
        ('group3', 'help text for g3', [cmd7]),
        ('group2', 'help text for g2', [cmd3, cmd4, cmd5, cmd1]),
    ]
    fake_summary = textwrap.indent(textwrap.dedent("""
        This is the summary for
        the whole program.
    """), "    ")
    global_options = [
        ('-h, --help', 'Show this help message and exit.'),
        ('-q, --quiet', 'Only show warnings and errors, not progress.'),
    ]

    with patch('charmcraft.helptexts.GENERAL_SUMMARY', fake_summary):
        text = get_full_help(command_groups, global_options)

    expected = textwrap.dedent("""\
        Usage:
            charmcraft [help] <command>

        Summary:
            This is the summary for
            the whole program.

        Global options:
            -h, --help:        Show this help message and exit.
            -q, --quiet:       Only show warnings and errors, not progress.

        Starter commands:
            cmd1:              Cmd help which is very long but whatever.
            cmd3:              Extremely super crazy long super crazy long super
                               crazy long super crazy long super crazy long
                               help.
            cmd6-really-long:  More help.
            command-2:         Cmd help.

        Commands can be classified as follows:
            group1:            cmd6-really-long, command-2
            group2:            cmd1, cmd3, cmd4, cmd5
            group3:            cmd7

        For more information about a command, run 'charmcraft help <command>'.
        For a summary of all commands, run 'charmcraft help --all'.
    """)
    assert text == expected


def test_detailed_help_text():
    """All different parts for the detailed help, showing all commands."""
    cmd1 = create_command('cmd1', 'Cmd help which is very long but whatever.', common_=True)
    cmd2 = create_command('command-2', 'Cmd help.', common_=True)
    cmd3 = create_command('cmd3', 'Extremely ' + 'super crazy long ' * 5 + ' help.', common_=True)
    cmd4 = create_command('cmd4', 'Some help.')
    cmd5 = create_command('cmd5', 'More help.')
    cmd6 = create_command('cmd6-really-long', 'More help.', common_=True)
    cmd7 = create_command('cmd7', 'More help.')

    command_groups = [
        ('group1', 'Group 1 description', [cmd6, cmd2]),
        ('group3', 'Group 3 help text', [cmd7]),
        ('group2', 'Group 2 stuff', [cmd3, cmd4, cmd5, cmd1]),
    ]
    fake_summary = textwrap.indent(textwrap.dedent("""
        This is the summary for
        the whole program.
    """), "    ")
    global_options = [
        ('-h, --help', 'Show this help message and exit.'),
        ('-q, --quiet', 'Only show warnings and errors, not progress.'),
    ]

    with patch('charmcraft.helptexts.GENERAL_SUMMARY', fake_summary):
        text = get_detailed_help(command_groups, global_options)

    expected = textwrap.dedent("""\
        Usage:
            charmcraft [help] <command>

        Summary:
            This is the summary for
            the whole program.

        Global options:
            -h, --help:        Show this help message and exit.
            -q, --quiet:       Only show warnings and errors, not progress.

        Commands can be classified as follows:

        Group 1 description:
            cmd6-really-long:  More help.
            command-2:         Cmd help.

        Group 3 help text:
            cmd7:              More help.

        Group 2 stuff:
            cmd3:              Extremely super crazy long super crazy long super
                               crazy long super crazy long super crazy long
                               help.
            cmd4:              Some help.
            cmd5:              More help.
            cmd1:              Cmd help which is very long but whatever.

        For more information about a specific command, run 'charmcraft help <command>'.
    """)
    assert text == expected


def test_command_help_text_no_parameters():
    """All different parts for a specific command help that doesn't have parameters."""
    overview = textwrap.dedent("""
        Quite some long text.

        Multiline!
    """)
    cmd1 = create_command('somecommand', 'Command one line help.', overview_=overview)
    cmd2 = create_command('other-cmd-2', 'Some help.')
    cmd3 = create_command('other-cmd-3', 'Some help.')
    cmd4 = create_command('other-cmd-4', 'Some help.')
    command_groups = [
        ('group1', 'help text for g1', [cmd1, cmd2, cmd4]),
        ('group2', 'help text for g2', [cmd3]),
    ]

    options = [
        ("-h, --help", "Show this help message and exit."),
        ("-q, --quiet", "Only show warnings and errors, not progress."),
        ("--name", "The name of the charm."),
        ("--revision", "The revision to release (defaults to latest)."),
    ]

    text = get_command_help(command_groups, cmd1('group1'), options)

    expected = textwrap.dedent("""\
        Usage:
            charmcraft somecommand [options]

        Summary:
            Quite some long text.

            Multiline!

        Options:
            -h, --help:   Show this help message and exit.
            -q, --quiet:  Only show warnings and errors, not progress.
            --name:       The name of the charm.
            --revision:   The revision to release (defaults to latest).

        See also:
            other-cmd-2
            other-cmd-4

        For a summary of all commands, run 'charmcraft help --all'.
    """)
    assert text == expected


def test_command_help_text_with_parameters():
    """All different parts for a specific command help that has parameters."""
    overview = textwrap.dedent("""
        Quite some long text.
    """)
    cmd1 = create_command('somecommand', 'Command one line help.', overview_=overview)
    cmd2 = create_command('other-cmd-2', 'Some help.')
    command_groups = [
        ('group1', 'help text for g1', [cmd1, cmd2]),
    ]

    options = [
        ("-h, --help", "Show this help message and exit."),
        ("name", "The name of the charm."),
        ("--revision", "The revision to release (defaults to latest)."),
        ("extraparam", "Another parameter.."),
        ("--other-option", "Other option."),
    ]

    text = get_command_help(command_groups, cmd1('group1'), options)

    expected = textwrap.dedent("""\
        Usage:
            charmcraft somecommand [options] name extraparam

        Summary:
            Quite some long text.

        Options:
            -h, --help:      Show this help message and exit.
            --revision:      The revision to release (defaults to latest).
            --other-option:  Other option.

        See also:
            other-cmd-2

        For a summary of all commands, run 'charmcraft help --all'.
    """)
    assert text == expected


def test_command_help_text_loneranger():
    """All different parts for a specific command that's the only one in its group."""
    overview = textwrap.dedent("""
        Quite some long text.
    """)
    cmd1 = create_command('somecommand', 'Command one line help.', overview_=overview)
    cmd2 = create_command('other-cmd-2', 'Some help.')
    command_groups = [
        ('group1', 'help text for g1', [cmd1]),
        ('group2', 'help text for g2', [cmd2]),
    ]

    options = [
        ("-h, --help", "Show this help message and exit."),
        ("-q, --quiet", "Only show warnings and errors, not progress."),
    ]

    text = get_command_help(command_groups, cmd1('group1'), options)

    expected = textwrap.dedent("""\
        Usage:
            charmcraft somecommand [options]

        Summary:
            Quite some long text.

        Options:
            -h, --help:   Show this help message and exit.
            -q, --quiet:  Only show warnings and errors, not progress.

        For a summary of all commands, run 'charmcraft help --all'.
    """)
    assert text == expected