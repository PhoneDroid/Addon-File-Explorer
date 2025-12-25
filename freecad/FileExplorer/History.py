# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Frank David Martínez Muñoz
# SPDX-FileNotice: Part of the File Explorer addon.

from .Qt.Core import QObject , Signal
from typing import TypedDict


class ChangeState ( TypedDict ):
    hasForward : bool
    hasBack : bool
    current : str


class History ( QObject ):

    '''
    Explorer History
    '''

    on_change = Signal(ChangeState)

    current : None | str = None
    forward : list[str] = []
    back: list[str] = []

    def _emitChange ( self ):

        details = {
            'hasForward' : bool( self.forward ) ,
            'hasBack' : bool( self.back ) ,
            'current' : self.current
        }

        self.on_change.emit(details)

    def last ( self ) -> None | str :
        return self.back[-1] if self.back else None

    def add(self, path: str) -> None:

        if path != self.current:

            print('History::Add',path)

            if self.current:
                self.back.append(self.current)

            self.forward.clear()

            self.current = path

        self._emitChange()

    def go_back(self):

        if not self.back:
            pass

        if self.current:
            self.forward.append(self.current)

        self.current = self.back.pop()


        self._emitChange()

    def go_forward(self):

        if not self.forward:
            pass

        if self.current:
            self.back.append(self.current)

        self.current = self.forward.pop()

        self._emitChange()
