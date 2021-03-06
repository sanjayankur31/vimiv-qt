# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Fixtures and bdd-like steps for usage during end2end testing."""

import os

from PyQt5.QtCore import Qt, QProcess
from PyQt5.QtWidgets import QApplication

import pytest
import pytest_bdd as bdd

import vimiv.gui.library
import vimiv.gui.thumbnail
import vimiv.gui.mainwindow
import vimiv.gui.commandline
import vimiv.gui.bar
import vimiv.gui.image
from vimiv import api
from vimiv.commands import runners
from vimiv.gui import statusbar
from vimiv.imutils import filelist


########################################################################################
#                                   Pytest fixtures                                    #
########################################################################################
@pytest.fixture()
def library():
    yield vimiv.gui.library.Library.instance


@pytest.fixture()
def thumbnail():
    yield vimiv.gui.thumbnail.ThumbnailView.instance


@pytest.fixture()
def mainwindow():
    yield vimiv.gui.mainwindow.MainWindow.instance


@pytest.fixture()
def commandline():
    yield vimiv.gui.commandline.CommandLine.instance


@pytest.fixture()
def bar():
    yield vimiv.gui.bar.Bar.instance


@pytest.fixture()
def image():
    yield vimiv.gui.image.ScrollableImage.instance


class Counter:
    """Counter class with the count command for simple testing of commands.

    Sole purpose is to provide a command whose result, namely increasing the number, is
    easily testable without depending on other vimiv features or commands. The number is
    stored as class attribute to avoid having to deal with class instances in the object
    registry.
    """

    number = 0

    def __init__(self):
        """Reset number when a new instance is created."""
        Counter.number = 0

    @staticmethod
    @api.commands.register()
    def count(number: int = 1, count: int = 1):
        """Helper command to increase a counter used for testing."""
        Counter.number += number * count


@pytest.fixture(autouse=True)
def counter():
    """Fixture to provide a clean counter class with the count command."""
    yield Counter()


###############################################################################
#                                    When                                     #
###############################################################################


@bdd.when(bdd.parsers.parse("I run {command}"))
def run_command(command):
    runners.run(command, mode=api.modes.current())


@bdd.when(bdd.parsers.parse("I press {keys}"))
def key_press(qtbot, keys):
    mode = api.modes.current()
    qtbot.keyClicks(mode.widget, keys)


@bdd.when(bdd.parsers.parse("I press <{modifier}>{keys}"))
def key_press_modifier(qtbot, keys, modifier):
    modifiers = {
        "ctrl": Qt.ControlModifier,
        "alt": Qt.AltModifier,
        "shift": Qt.ShiftModifier,
    }
    mode = api.modes.current()
    qtbot.keyClicks(mode.widget, keys, modifier=modifiers[modifier])


@bdd.when("I activate the command line")
def activate_commandline(commandline, qtbot):
    """Needed as passing return as a string is not possible."""
    qtbot.keyClick(commandline, Qt.Key_Return)
    qtbot.wait(10)


@bdd.when(bdd.parsers.parse("I enter {mode} mode"))
def enter_mode(mode):
    api.modes.get_by_name(mode).enter()


@bdd.when(bdd.parsers.parse("I leave {mode} mode"))
def leave_mode(mode):
    api.modes.get_by_name(mode).leave()


@bdd.when(bdd.parsers.parse("I resize the window to {size}"))
def resize_main_window(mainwindow, size):
    width = int(size.split("x")[0])
    height = int(size.split("x")[1])
    mainwindow.resize(width, height)


@bdd.when("I wait for the command to complete")
def wait_for_external_command(qtbot):
    """Wait until the external process has completed."""
    runner = runners.external._impl
    if runner is None:
        return

    def external_finished():
        assert runner.state() == QProcess.NotRunning, "external command timed out"

    qtbot.waitUntil(external_finished, timeout=30000)


@bdd.when("I wait for the working directory handler")
def wait_for_working_directory_handler(qtbot):
    with qtbot.waitSignal(api.working_directory.handler.changed):
        pass


###############################################################################
#                                    Then                                     #
###############################################################################


@bdd.then("no crash should happen")
def no_crash(qtbot):
    """Don't do anything, exceptions fail the test anyway."""
    qtbot.wait(1)


@bdd.then(bdd.parsers.parse("the message\n'{message}'\nshould be displayed"))
def check_statusbar_message(qtbot, message):
    bar = statusbar.statusbar

    def check_status():
        assert message == bar.message.text(), "Message expected: '{message}'"

    qtbot.waitUntil(check_status, timeout=100)
    assert bar.stack.currentWidget() == bar.message


@bdd.then(bdd.parsers.parse("the {position} status should include {text}"))
def check_left_status(qtbot, position, text):
    bar = statusbar.statusbar
    message = f"statusbar {position} should include {text}"

    def check_status():
        assert text in getattr(bar.status, position).text(), message

    qtbot.waitUntil(check_status, timeout=100)
    assert bar.stack.currentWidget() == bar.status


@bdd.then("a message should be displayed")
def check_a_statusbar_message(qtbot):
    bar = statusbar.statusbar

    def check_status():
        assert bar.message.text(), "Any message expected"

    qtbot.waitUntil(check_status, timeout=100)
    assert bar.stack.currentWidget() == bar.message


@bdd.then("no message should be displayed")
def check_no_statusbar_message(qtbot):
    bar = statusbar.statusbar

    def check_status():
        assert not bar.message.text(), "No message expected"

    qtbot.waitUntil(check_status, timeout=100)
    assert bar.stack.currentWidget() == bar.status


@bdd.then(bdd.parsers.parse("the working directory should be {basename}"))
def check_working_directory(basename):
    assert os.path.basename(os.getcwd()) == basename


@bdd.then("the window should be fullscreen")
def check_fullscreen(mainwindow):
    assert mainwindow.isFullScreen()


@bdd.then("the window should not be fullscreen")
def check_not_fullscreen(mainwindow):
    assert not mainwindow.isFullScreen()


@bdd.then(bdd.parsers.parse("the mode should be {mode}"))
def check_mode(mode, qtbot):
    mode = api.modes.get_by_name(mode)
    assert api.modes.current() == mode, f"Modehandler did not switch to {mode.name}"


@bdd.then(bdd.parsers.parse("the library row should be {row}"))
def check_row_number(library, row):
    assert library.row() + 1 == int(row)


@bdd.then(bdd.parsers.parse("the image should have the index {index}"))
def check_image_index(index):
    assert filelist.get_index() == index


@bdd.given("I enter thumbnail mode")
def enter_thumbnail(thumbnail):
    api.modes.THUMBNAIL.enter()
    thumbnail.setFixedWidth(400)  # Make sure width is as expected


@bdd.then(bdd.parsers.parse("the thumbnail number {N:d} should be selected"))
def check_selected_thumbnail(thumbnail, qtbot, N):
    assert thumbnail.currentRow() + 1 == N


@bdd.then(bdd.parsers.parse("the pop up '{title}' should be displayed"))
def check_popup_displayed(title):
    for window in QApplication.topLevelWindows():
        if window.title() == title:
            window.close()
            return
    raise AssertionError(f"Window '{title}' not found")


@bdd.then(bdd.parsers.parse("the filelist should contain {number} images"))
def check_filelist_length(number):
    assert filelist.total() == number


@bdd.then(bdd.parsers.parse("the file {name} should exist"))
@bdd.then("the file <name> should exist")
def check_file_exists(name):
    assert os.path.isfile(name)


@bdd.then(bdd.parsers.parse("the file {name} should not exist"))
def check_not_file_exists(name):
    assert not os.path.isfile(name)


@bdd.then(bdd.parsers.parse("the directory {name} should exist"))
def check_directory_exists(name):
    assert os.path.isdir(name)


@bdd.then(bdd.parsers.parse("the directory {name} should not exist"))
def check_not_directory_exists(name):
    assert not os.path.isdir(name)


@bdd.then(bdd.parsers.parse("the count should be {number:d}"))
def check_count(counter, number):
    assert counter.number == number


@bdd.then(bdd.parsers.parse("the text in the command line should be {text}"))
def check_commandline_text(commandline, text):
    assert commandline.text() == text
