# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Frank David Martínez Muñoz
# SPDX-FileNotice: Part of the File Explorer addon.

"""
Explorer Styling
"""

from .Qt.Widgets import QApplication, QStyle
from .Qt.Gui import QIcon


fromTheme = QIcon.fromTheme
pixmaps = QStyle.StandardPixmap
asIcon = QApplication.style().standardIcon


class Icons:
    FavoriteDir = fromTheme("folder", asIcon(pixmaps.SP_DirIcon))
    RootDir = asIcon(pixmaps.SP_ComputerIcon)
    HomeDir = fromTheme("user-home", asIcon(pixmaps.SP_DirHomeIcon))

    SysOpen = fromTheme("document-open", asIcon(pixmaps.SP_DirOpenIcon))
    Import = asIcon(pixmaps.SP_ArrowForward)
    Copy = fromTheme("edit-copy", asIcon(pixmaps.SP_CommandLink))

    Macros = asIcon(pixmaps.SP_FileIcon)

    NavForward = fromTheme("go-next", asIcon(pixmaps.SP_ArrowForward))
    NavBack = fromTheme("go-previous", asIcon(pixmaps.SP_ArrowBack))
    NavUp = fromTheme("go-up", asIcon(pixmaps.SP_ArrowUp))
