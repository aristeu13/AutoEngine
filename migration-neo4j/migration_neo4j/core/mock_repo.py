from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from migration_neo4j.domains.file.file_domain import MigrationFile
    from migration_neo4j.domains.folder.folder_domain import Folder


class MockStorage:
    _instance: "MockStorage | None" = None
    data: dict[str, "MigrationFile | Folder | None"]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MockStorage, cls).__new__(cls)
            cls._instance.data = {}
        return cls._instance

    def set(self, key: str, value: "MigrationFile | Folder"):
        self.data[key] = value

    def get(self, key) -> "MigrationFile | Folder | None":
        return self.data.get(key)

    def exists(self, key) -> bool:
        return key in self.data

    def items(self):
        return self.data.items()

    def reset(self):
        self.data = {}
