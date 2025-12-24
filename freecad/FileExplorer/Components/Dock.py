
from __future__ import annotations

import FreeCADGui as Gui

from .Explorer import Explorer
from ..Intl import tr

from ..Qt.Widgets import QDockWidget , QWidget
from ..Qt.Core import Qt


class Dock(QDockWidget):
    """
    Dockable container for File Explorer.
    """

    explorer : Explorer

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(tr("FileExplorerExt", "File Explorer"), parent)
        self.explorer = Explorer(self)
        self.setWidget(self.explorer)
        self.setObjectName("FileExplorerExt_Dock")


def show() -> None:
    window = Gui.getMainWindow()
    dock = Dock(window)
    window.__FileExplorerExt__ = dock
    window.addDockWidget(Qt.LeftDockWidgetArea, dock)
