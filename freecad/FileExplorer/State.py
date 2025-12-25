# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Frank David Martínez Muñoz
# SPDX-FileNotice: Part of the File Explorer addon.

import json
from pathlib import Path

import FreeCAD as App

from .History import History

from .Qt.Core import QObject, Signal, QUrl
from .Qt.Gui import QDesktopServices


class State ( QObject ):

    '''
    Explorer State
    '''

    user_navigate: Signal = Signal(str)
    root_changed: Signal = Signal(str,bool)
    path_changed: Signal = Signal(str)

    _current_path: str
    _history: History

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._current_path = ""
        self._history = History()
        self.root_changed.connect(self.onRootChanged)

    def get_last_path(self) -> str:
        return self._current_path or str(Path.home())

    def open_with_sys_app(self, path: str) -> None:
        url = QUrl.fromLocalFile(path)
        QDesktopServices.openUrl(url)

    def onRootChanged(self, path: str,initial : bool) -> None:

        # print('State::onRootChanged',initial,path)

        if not initial:
            self._history.add(path)

    def navigate_back(self) -> None:
        # print('State::NavigateBack')
        self._history.go_back()

    def navigate_forward(self) -> None:
        # print('State::NavigateForward')
        self._history.go_forward()

    def get_favorites(self) -> list[tuple[str, str]]:
        path = Path(App.getUserConfigDir()) / "file_explorer.json"
        if path.exists():
            data = json.loads(path.read_text())
        else:
            data = {}
        favorites = data.get("favorites", {})
        return list(favorites.items())

    def save_favorites(self, data: list[tuple[str, str]]) -> None:
        path = Path(App.getUserConfigDir()) / "file_explorer.json"
        if path.exists():
            s_data = json.loads(path.read_text())
        else:
            s_data = {}
        s_data["favorites"] = dict(data)
        path.write_text(json.dumps(s_data))
