# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Frank David Martínez Muñoz
# SPDX-FileNotice: Part of the File Explorer addon.

"""
FileSystem Helpers
"""

from pathlib import Path
from shutil import copy2
from re import match

import FreeCADGui as Gui
import FreeCAD as App

from .Qt.Gui import QImageReader

Supported_Formats = set(format.toStdString() for format in QImageReader.supportedImageFormats())


def getSuffix(file: str) -> str:
    return Path(file).suffix[1:]


def isSupportedImage(file: str) -> bool:
    return getSuffix(file) in Supported_Formats


def isProject(file: str) -> bool:
    return getSuffix(file) == "fcstd"


def getImporter(file: str) -> str | None:
    suffix = getSuffix(file)

    modules = App.getImportType(suffix)

    if type(modules) == list:
        return modules[0]

    return None


def open_file(file: str) -> None:
    if isProject(file):
        App.openDocument(file)
        return

    module = getImporter(file)

    if not module:
        App.Console.PrintWarning(f"File type not supported: {file}\n")
        return

    try:
        from freecad import module_io

        module_io.OpenInsertObject(module, file, "open")

    except ImportError:
        Gui.insert(file)


def import_file(file: str) -> None:
    name = App.ActiveDocument.Name if App.ActiveDocument else None

    if not name:
        return

    if isProject(file):
        Gui.insert(file, name)

    module = getImporter(file)

    if not module:
        App.Console.PrintWarning(f"File type not supported: {file}\n")
        return

    try:
        from freecad import module_io

        module_io.OpenInsertObject(
            module,
            file,
            "insert",
            name,
        )

    except ImportError:
        Gui.insert(file, name)


def duplicate_file(file: str) -> bool:
    path = Path(file)

    try:
        if not path.exists():
            return False

        if not path.is_file():
            return False

        suffix = path.suffix
        stem = path.stem

        matched = match(r"(.*?)(\d+)$", stem)

        index = 1
        stem += "."

        if matched:
            stem, index = matched.groups()
            index = int(index) + 1

        copy = path.parent / f"{stem}{index}{suffix}"

        while copy.exists():
            index += 1
            copy = path.parent / f"{stem}{index}{suffix}"

        copy2(path, copy)

        return True

    except Exception as exception:
        print("Failed to duplicate file", file, exception)

        return False
