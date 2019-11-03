# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions to help with XDG_USER_* settings."""

import os

from PyQt5.QtCore import QStandardPaths

import vimiv


def _qstandardpath(location, *paths: str) -> str:
    return os.path.join(QStandardPaths.writableLocation(location), *paths)


def user_data_dir(*paths: str) -> str:
    return _qstandardpath(QStandardPaths.GenericDataLocation, *paths)


def user_config_dir(*paths: str) -> str:
    return _qstandardpath(QStandardPaths.GenericConfigLocation, *paths)


def user_cache_dir(*paths: str) -> str:
    return _qstandardpath(QStandardPaths.GenericCacheLocation, *paths)


def vimiv_data_dir(*paths: str) -> str:
    return user_data_dir(vimiv.__name__, *paths)


def vimiv_cache_dir(*paths: str) -> str:
    return user_cache_dir(vimiv.__name__, *paths)


def vimiv_config_dir(*paths: str) -> str:
    return user_config_dir(vimiv.__name__, *paths)
