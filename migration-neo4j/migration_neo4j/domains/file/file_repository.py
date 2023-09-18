from abc import ABC, abstractmethod
from pathlib import Path
from migration_neo4j.core.mock_repo import MockStorage
from migration_neo4j.domains.file.file_domain import MigrationFile
import os

from migration_neo4j.domains.folder.folder_domain import Folder


class IMigrationFileRepository(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def read(self, path: str) -> MigrationFile:
        pass

    @abstractmethod
    def write(self, path: str, file: MigrationFile) -> None:
        pass


class MigrationFileRepository(IMigrationFileRepository):
    def __init__(self) -> None:
        super().__init__()

    def read(self, path: str) -> MigrationFile:
        with open(path, "r") as f:
            content = f.read()
        name = os.path.basename(path)
        return MigrationFile(name=name, content=content)

    def write(self, path: str, file: MigrationFile) -> None:
        with open(path, "w") as f:
            f.write(file.content)


class MigrationFileRepositoryMock(IMigrationFileRepository):
    def __init__(self) -> None:
        super().__init__()
        self.storage = MockStorage()

    def read(self, path: str) -> MigrationFile:
        file = self.storage.get(path)
        if file is None:
            raise FileNotFoundError(f"file {path} not found")
        if not isinstance(file, MigrationFile):
            raise TypeError(f"file {path} is not a MigrationFile")
        return file

    def write(self, path: str, file: MigrationFile) -> None:
        for parent in Path(path).parents:
            if not self.storage.exists(parent):
                self.storage.set(str(parent), Folder(name=parent.name))
        self.storage.set(path, file)
