# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Frank David Martínez Muñoz
# SPDX-FileNotice: Part of the File Explorer addon.

import zipfile

from ..Files import isProject, isSupportedImage
from ..State import State

from ..Qt.Widgets import QWidget, QLabel
from ..Qt.Core import QFileInfo, QSize, Qt
from ..Qt.Gui import QPixmap


class PreviewPanel(QLabel):
    """
    Preview Widget
    """

    _state: State

    def __init__(self, state: State, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("FileExplorer_Preview")
        self._state = state
        self.init_ui()

        state.path_changed.connect(self.onPathChanged)
        state.root_changed.connect(lambda: self.setVisible(False))

    def onPathChanged(self, path: str) -> None:
        self.update_preview(path)

    def init_ui(self) -> None:
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setVisible(False)
        self.setStyleSheet("QLabel { background-color: white; }")

    def update_preview(self, file: str) -> None:
        self.setVisible(False)

        try:
            info = QFileInfo(file)

            if not info.exists():
                return

            if info.isDir():
                return

            file = info.absoluteFilePath()

            if isSupportedImage(file):
                pixmap = QPixmap(file)
                if not pixmap.isNull():
                    self.show_image_preview(pixmap)
                    return

            if isProject(file):
                pixmap = self.get_fcstd_preview(file)
                if pixmap and not pixmap.isNull():
                    self.show_image_preview(pixmap)
                    return

        except Exception as exception:
            print("Failed to update preview", file, exception)
            self.setVisible(True)
            return

    def show_image_preview(self, pixmap: QPixmap) -> None:
        """Display image preview scaled to available width."""
        target_width = max(self.width() - 24, 150)
        scaled = pixmap.scaled(
            QSize(target_width, target_width),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.setPixmap(scaled)
        self.setVisible(True)

    def get_fcstd_preview(self, file_path: str) -> QPixmap | None:
        """Load Thumbnail.png from a FreeCAD .FCStd file if available."""
        try:
            with zipfile.ZipFile(file_path, "r") as zf:
                thumb_name = "thumbnails/Thumbnail.png"
                if thumb_name not in zf.namelist():
                    return None
                data = zf.read(thumb_name)
                pixmap = QPixmap()
                if pixmap.loadFromData(data):
                    return pixmap
        except (zipfile.BadZipFile, OSError, KeyError):
            return None
        return None
