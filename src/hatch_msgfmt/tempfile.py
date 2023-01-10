from typing import Union
from pathlib import Path
from tempfile import mkstemp
import os
from subprocess import run, DEVNULL
from weakref import finalize

class UnopenedTemporaryFile:
    '''Like NamedTemporaryFile, but not open by default.
    '''
    def __init__(self, *args, **kwargs):
        handle, pathname = mkstemp(*args, **kwargs)
        os.close(handle)
        self.name: Union[str, bytes] = pathname
        self.__str = None
        self.__bytes = None
        self.__path = None

        self.cleanup = finalize(self, lambda path: path.unlink(), self.path)

    def __enter__(self) -> Path:
        assert self.cleanup.alive, 'File has been deleted'
        return self.path

    def __exit__(self, type, value, traceback) -> None:
        assert self.cleanup.alive, 'File has been deleted'
        self.cleanup()
        self.__dead = True

    def __str__(self) -> str:
        assert self.cleanup.alive, 'File has been deleted'
        if self.__str is None:
            if isinstance(self.name, str):
                self.__str = self.name
            else:
                self.__str = os.fsdecode(self.name)

        return self.__str

    def __bytes__(self) -> bytes:
        assert self.cleanup.alive, 'File has been deleted'
        if self.__bytes == None:
            if isinstance(self.name, bytes):
                self.__bytes = self.name
            else:
                self.__bytes = os.fsencode(self.name)

        return self.__bytes

    @property
    def path(self) -> Path:
        assert self.cleanup.alive, 'File has been deleted'
        if self.__path is None:
            self.__path = Path(str(self))

        return self.__path
