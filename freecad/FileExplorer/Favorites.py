# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Frank David Martínez Muñoz
# SPDX-FileNotice: Part of the File Explorer addon.

from dataclasses import dataclass
from pathlib import Path

from .Style import Icons
from .Intl import tr

from .Qt.Core import (
    QAbstractListModel,
    QPersistentModelIndex,
    QModelIndex,
    QObject,
    QDir,
    Qt,
)

Role = Qt.ItemDataRole

import FreeCAD as App


@dataclass
class Favorite:
    path: str
    name: str | None = None
    kind: str = "user"
    order: int = 2

    def __post_init__(self) -> None:
        if not self.name:
            self.name = Path(self.path).stem


RootDir = Favorite(
    path="",
    name=tr("FileExplorer", "This PC"),
    kind="root",
    order=0,
)

HomeDir = Favorite(
    path=QDir.homePath(),
    name=tr("FileExplorer", "Home"),
    kind="home",
    order=1,
)

MacrosDir = Favorite(
    path=App.getUserMacroDir(True),
    name=tr("FileExplorer", "Macros"),
    kind="macro",
    order=1,
)


class DuplicatedFavoriteError(Exception):
    pass


class FavoritesModel(QAbstractListModel):
    """
    Favorites Model.
    """

    def __init__(
        self,
        user: list[Favorite],
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._items: list[Favorite] = [RootDir, HomeDir, MacrosDir] + user
        self.icons = {
            "root": Icons.RootDir,
            "home": Icons.HomeDir,
            "macro": Icons.Macros,
            "user": Icons.FavoriteDir,
        }

    def rowCount(self, parent: QPersistentModelIndex | QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._items)

    def data(
        self,
        index: QPersistentModelIndex | QModelIndex,
        role: int = Role.DisplayRole,
    ) -> object:
        if not index.isValid() or index.row() >= len(self._items):
            return None

        item = self._items[index.row()]
        match role:
            case Role.DisplayRole:
                return item.name
            case Role.DecorationRole:
                return self.icons.get(item.kind, None)
            case Role.UserRole:
                return item
            case Role.ToolTipRole:
                return item.path
            case _:
                return None

    def addItem(self, fav: Favorite) -> None:
        for it in self._items:
            if it.path == fav.path:
                raise DuplicatedFavoriteError

        row = len(self._items)
        self.beginInsertRows(QModelIndex(), row, row)
        self._items.append(fav)
        self.endInsertRows()

    def removeItem(self, row: int) -> None:
        if 0 <= row < len(self._items):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._items[row]
            self.endRemoveRows()

    def clear(self) -> None:
        if self._items:
            self.beginResetModel()
            self._items.clear()
            self.endResetModel()

    def setItems(self, items: list[Favorite]) -> None:
        self.beginResetModel()
        self._items = list(items)
        self.endResetModel()

    def getItem(self, row: int) -> Favorite | None:
        if 0 <= row < len(self._items):
            return self._items[row]
        return None

    def contains_name(self, name: str) -> bool:
        for fav in self._items:
            if name == fav.name:
                return True
        return False

    def findIndex(self, path: str) -> QModelIndex | None:
        for row, fav in enumerate(self._items):
            if path == fav.path:
                return self.index(row, 0)
        return None

    def get_state(self) -> list[tuple[str, str]]:
        return [(f.path, f.name) for f in self._items if f.kind == "user" and f.name]

