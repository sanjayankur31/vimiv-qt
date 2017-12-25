# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Class to play a slideshow."""

from PyQt5.QtCore import QTimer, pyqtSignal

from vimiv.commands import commands
from vimiv.config import settings, keybindings
from vimiv.gui import statusbar
from vimiv.utils import objreg


class Slideshow(QTimer):
    """Slideshow class inheriting from QTimer.

    Signals:
        next_im: Emitted when the next image should be displayed.
    """

    next_im = pyqtSignal()

    @objreg.register("slideshow")
    def __init__(self):
        super().__init__()
        settings.signals.changed.connect(self._on_settings_changed)
        # TODO get default somehow
        self.setInterval(2000)

    @keybindings.add("s", "slideshow", mode="image")
    @commands.register(instance="slideshow", mode="image", count=0)
    def slideshow(self, count):
        """Toggle slideshow."""
        if count:
            self.setInterval(1000 * count)
        elif self.isActive():
            self.stop()
        else:
            self.start()

    def timerEvent(self, event):
        """Emit next_im signal on timer tick."""
        self.next_im.emit()
        statusbar.update()

    @statusbar.module("{slideshow_delay}", instance="slideshow")
    def get_delay(self):
        """Return current delay if slideshow is running for statusbar."""
        if self.isActive():
            delay = self.interval() / 1000
            return "%.1fs" % (delay)
        return ""

    @statusbar.module("{slideshow_indicator}", instance="slideshow")
    def running_indicator(self):
        """Return indicator if slideshow is running for statusbar."""
        if self.isActive():
            return settings.get_value("slideshow.indicator")
        return ""

    def _on_settings_changed(self, setting, new_value):
        if setting == "slideshow.delay":
            self.setInterval(new_value * 1000)