# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Frank David Martínez Muñoz
# SPDX-FileNotice: Part of the File Explorer addon.

'''
History Navigation
'''


class History:

    forward : list[str] = []
    back: list[str] = []

    def last ( self ) -> None | str :
        return self.back[-1] if self.back else None

    def add(self, path: str) -> None:
        if self.last() != path:
            self.back.append(path)

    def go_back(self) -> str | None:

        if not self.back:
            return None

        item = self.back.pop()
        self.forward.append(item)
        return item

    def go_forward(self) -> str | None:

        if not self.forward:
            return None

        item = self.forward.pop()
        self.back.append(item)
        return item
