# -*- coding: utf-8 -*-
"""Manage shell commands."""
import subprocess


def execute(command):
    """Run command (a list of arguments) and return (code, stdout, stderr).

    >>> from diecutter.utils.sh import execute
    >>> code, stdout, stderr = execute(['echo', '-n', 'Hello world!'])
    >>> code
    0
    >>> stdout
    'Hello world!'
    >>> stderr
    ''

    """
    process = subprocess.Popen(command,
                               stdin=None,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               shell=False)
    return (process.wait(), process.stdout.read(), process.stderr.read())
