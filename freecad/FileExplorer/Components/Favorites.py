# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Frank David Martínez Muñoz
# SPDX-FileNotice: Part of the File Explorer addon.

from ..Favorites import DuplicatedFavoriteError, FavoritesModel, Favorite
from ..History import ChangeState
from ..State import State
from ..Intl import tr

from ..Qt.Widgets import (
    QAbstractItemView,
    QInputDialog,
    QMessageBox,
    QListView,
    QLineEdit,
    QWidget,
    QMenu,
)
from ..Qt.Core import (
    QItemSelectionModel,
    QModelIndex,
    QPoint,
    QSize,
    Qt,
)
from ..Qt.Gui import QDragEnterEvent, QDragMoveEvent, QDropEvent

Role = Qt.ItemDataRole


class FavoritesWidget(QListView):
    """
    Favorites Widget
    """

    _model: FavoritesModel
    _state: State

    def __init__(
        self,
        state: State,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("FileExplorer_Favorites")
        user_data = [Favorite(path, name) for path, name in state.get_favorites()]
        self._model = FavoritesModel(user_data, self)
        self._state = state
        self.setModel(self._model)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_context_menu)
        self.setIconSize(QSize(16, 16))
        self.setSpacing(2)

        self.activated.connect(self.on_activated)
        self.clicked.connect(self.on_activated)

        state._history.on_change.connect(self.onHistoryChange)

    def onHistoryChange(self, details: ChangeState) -> None:
        path = details["current"]

        # print('Favorites::UserNavigate',path)

        index = self._model.findIndex(path)

        if index:
            self.selectIndex(index)

    def selectIndex(self, index: QModelIndex):
        if not index.isValid():
            pass

        self.selectionModel().select(index, QItemSelectionModel.SelectionFlag.ClearAndSelect)

    def on_activated(self, index: QModelIndex) -> None:
        if not index.isValid():
            return

        favorite = self._model.getItem(index.row())

        if not favorite:
            return

        path = favorite.path

        self._state.user_navigate.emit(path)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        mime_data = event.mimeData()

        # Handle URLs (from file system)
        if mime_data.hasUrls():
            for url in mime_data.urls():
                if path := url.toLocalFile():
                    self.add_path(path)
            event.acceptProposedAction()

        # Handle text (file path from tree view)
        elif mime_data.hasText():
            path = mime_data.text()
            if path:
                self.add_path(path)
            event.acceptProposedAction()

    def add_path(self, path: str) -> None:
        try:
            self._model.addItem(Favorite(path))
            self._state.save_favorites(self._model.get_state())
        except DuplicatedFavoriteError:
            QMessageBox.warning(
                self,
                tr("FileExplorer", "Duplicated"),
                tr("FileExplorer", "Duplicated favorite"),
            )

    def on_context_menu(self, position: QPoint) -> None:
        index = self.indexAt(position)
        if not index.isValid():
            return

        fav = self._model.getItem(index.row())

        if fav and fav.kind != "user":
            return

        menu = QMenu(self)

        menu.addAction(
            tr("FileExplorer", "Rename"),
            lambda: self.rename_favorite(index),
        )

        menu.addAction(
            tr("FileExplorer", "Remove from Favorites"),
            lambda: self.remove_favorite(index),
        )

        menu.exec(self.mapToGlobal(position))

    def remove_favorite(self, index: QModelIndex) -> None:
        if not index.isValid():
            return
        fav = self._model.getItem(index.row())
        if fav and fav.kind == "user":
            self._model.removeItem(index.row())
            self._state.save_favorites(self._model.get_state())

    def rename_favorite(self, index: QModelIndex) -> None:
        if not index.isValid():
            return

        row = index.row()
        fav = self._model.getItem(row)

        if not fav:
            return

        name = fav.name

        if not name:
            return

        new_name, ok = QInputDialog.getText(
            self,
            tr("FileExplorer", "Rename Favorite"),
            tr("FileExplorer", "Enter new name:"),
            QLineEdit.EchoMode.Normal,
            name,
        )

        if ok and new_name and new_name != fav.name and not self._model.contains_name(new_name):
            fav.name = new_name
            self._state.save_favorites(self._model.get_state())
            self._model.dataChanged.emit(index, index)
        else:
            QMessageBox.warning(
                self,
                tr("FileExplorer", "File Explorer"),
                tr("FileExplorer", "Cannot rename favorite"),
            )
