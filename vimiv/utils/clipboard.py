# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Copy to and paste from system clipboard."""

import os

from PyQt5.QtGui import QGuiApplication, QClipboard

from vimiv import app, api
from vimiv.config import keybindings
from vimiv.utils import pathreceiver


def init():
    """Initialize clipboard commands."""
    # Currently does not do anything but the commands need to be registered by
    # an import. May become useful in the future.


@keybindings.add("yA", "copy-name --abspath --primary")
@keybindings.add("yY", "copy-name --primary")
@keybindings.add("ya", "copy-name --abspath")
@keybindings.add("yy", "copy-name")
@api.commands.register()
def copy_name(abspath: bool = False, primary: bool = False):
    """Copy name of current path to system clipboard.

    **syntax:** ``:copy-name [--abspath] [--primary]``

    optional arguments:
        * ``--abspath``: Copy absolute path instead of basename.
        * ``--primary``: Copy to primary selection.
    """
    clipboard = QGuiApplication.clipboard()
    mode = QClipboard.Selection if primary else QClipboard.Clipboard
    path = pathreceiver.current()
    name = path if abspath else os.path.basename(path)
    clipboard.setText(name, mode=mode)


@keybindings.add("PP", "paste-name --primary")
@keybindings.add("Pp", "paste-name")
@api.commands.register()
def paste_name(primary: bool = True):
    """Paste path from clipboard to open command.

    **syntax:** ``:paste-name [--primary]``

    optional arguments:
        * ``--primary``: Paste from  primary selection.
    """
    clipboard = QGuiApplication.clipboard()
    mode = QClipboard.Selection if primary else QClipboard.Clipboard
    app.open(clipboard.text(mode=mode))
