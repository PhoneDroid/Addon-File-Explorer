# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Frank David Martínez Muñoz
# SPDX-FileNotice: Part of the File Explorer addon.

from __future__ import annotations

from pathlib import Path

from ..History import ChangeState
from ..State import State
from ..Style import Icons
from ..Intl import tr

from .Favorites import FavoritesWidget
from .Preview import PreviewPanel
from .Tree import FileTree

from ..Qt.Widgets import (
    QGraphicsOpacityEffect,
    QWidgetAction,
    QPushButton,
    QVBoxLayout,
    QStatusBar,
    QLineEdit,
    QSplitter,
    QToolBar,
    QWidget,
)
from ..Qt.Core import Qt
from ..Qt.Gui import QIcon


class Explorer(QWidget):
    """
    Explorer Widget
    """

    _state: State

    favorites: FavoritesWidget
    preview: PreviewPanel
    status: QStatusBar
    tree: FileTree

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._state = State()
        self.init_ui()

        self._state.root_changed.connect(lambda: self.status.showMessage(self.tree.root()))

        self._state.root_changed.emit(self.tree.root(), True)
        self._state._history._emitChange()

    def build_sidebar(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(self.favorites)
        layout.addWidget(self.preview)
        layout.setContentsMargins(0, 0, 0, 0)
        return container

    def build_top_toolbar(self) -> QToolBar:
        toolbar = QToolBar(self)
        toolbar.setObjectName("FileExplorer_ToolBar")

        def action(onClick: object, icon: QIcon, text: str):
            button = QPushButton()
            button.clicked.connect(onClick)
            button.setAutoFillBackground(True)
            button.setToolTip(text)
            button.setIcon(icon)

            action = QWidgetAction(toolbar)
            action.setDefaultWidget(button)

            toolbar.addAction(action)

            return action

        action_back = action(
            onClick=self._state.navigate_back, icon=Icons.NavBack, text=tr("FileExplorer", "Back")
        )

        action_up = action(onClick=self.tree.go_up, icon=Icons.NavUp, text=tr("FileExplorer", "Up"))

        action_forward = action(
            onClick=self._state.navigate_forward,
            icon=Icons.NavForward,
            text=tr("FileExplorer", "Forward"),
        )

        def setActionState(action: QWidgetAction, enabled: bool):
            action.setEnabled(enabled)

            opacity = 1.0 if enabled else 0.5

            effect = QGraphicsOpacityEffect(self)
            effect.setOpacity(opacity)

            widget = action.defaultWidget()

            widget.setGraphicsEffect(effect)

        def onRootChanged():
            file = self.tree.root()

            path = Path(file)

            enabled = file != path.root

            setActionState(action_up, enabled)

        self._state.root_changed.connect(onRootChanged)

        def on_history_change(details: ChangeState):
            setActionState(action_forward, details["hasForward"])
            setActionState(action_back, details["hasBack"])

        self._state._history.on_change.connect(on_history_change)

        filter_input = QLineEdit(self)
        filter_input.setPlaceholderText(tr("FileExplorer", "Filter..."))
        filter_input.textChanged.connect(self.on_filter_changed)
        toolbar.addSeparator()
        toolbar.addWidget(filter_input)
        return toolbar

    def init_ui(self) -> None:
        self.tree = FileTree(self._state, self)
        self.preview = PreviewPanel(self._state, self)
        self.favorites = FavoritesWidget(self._state, self)
        left_sidebar = self.build_sidebar()
        top_toolbar = self.build_top_toolbar()
        self.status = QStatusBar(self)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_sidebar)
        splitter.addWidget(self.tree)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 8)

        layout = QVBoxLayout(self)
        layout.addWidget(top_toolbar, stretch=0)
        layout.addWidget(splitter, stretch=1)
        layout.addWidget(self.status, stretch=0)
        self.setLayout(layout)

    def on_filter_changed(self, text: str):
        self.tree.setNameFilter(text)
