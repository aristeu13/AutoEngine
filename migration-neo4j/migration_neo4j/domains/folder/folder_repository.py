from abc import ABC, abstractmethod
import os
from pathlib import Path
from migration_neo4j.core.mock_repo import MockStorage
from migration_neo4j.domains.file.file_domain import MigrationFile
from migration_neo4j.domains.file.file_repository import IMigrationFileRepository

from migration_neo4j.domains.folder.folder_domain import Folder


class IFolderRepository(ABC):
    def __init__(
        self,
        migration_file_repository: "IMigrationFileRepository",
    ) -> None:
        self.migration_file_repository = migration_file_repository
        super().__init__()

    @abstractmethod
    def read(self, path: str) -> Folder:
        pass

    @abstractmethod
    def write(self, path: str) -> None:
        pass


class FolderRepository(IFolderRepository):
    def __init__(
        self,
        migration_file_repository: "IMigrationFileRepository",
    ) -> None:
        super().__init__(migration_file_repository)

    def read(self, path: str) -> Folder:
        if not os.path.isdir(path):
            raise NotADirectoryError(f"{path} is not a directory")
        folder = Folder(name=os.path.basename(path))
        for name in os.listdir(path):
            subpath = os.path.join(path, name)
            if os.path.isfile(subpath):
                file = self.migration_file_repository.read(subpath)
                folder.add_file(file)
            elif os.path.isdir(subpath):
                folder.add_subfolder(self.read(subpath))
        return folder

    def write(self, path: str) -> None:
        os.makedirs(path, exist_ok=True)


class FolderRepositoryMock(IFolderRepository):
    def __init__(self, migration_file_repository: IMigrationFileRepository) -> None:
        super().__init__(migration_file_repository)
        self.storage = MockStorage()

    def _is_childpath(self, path: str, children_path: str) -> bool:
        return (
            path != children_path
            and Path(path) in Path(children_path).parents
            and len(Path(path).parts) + 1 == len(Path(children_path).parts)
        )

    def read(self, path: str) -> Folder:
        folder = self.storage.get(path)
        if folder is None or isinstance(folder, MigrationFile):
            raise NotADirectoryError(f"{path} is not a directory")

        for children_path, item in self.storage.items():
            if self._is_childpath(path, children_path):
                if isinstance(item, MigrationFile):
                    folder.add_file(item)
                elif isinstance(item, Folder):
                    folder.add_subfolder(item)
                    self.read(children_path)
        return folder

    def write(self, path: str) -> None:
        for parent in Path(path).parents:
            if not self.storage.exists(str(parent)):
                self.storage.set(str(parent), Folder(name=os.path.basename(parent)))
        self.storage.set(path, Folder(name=os.path.basename(path)))
