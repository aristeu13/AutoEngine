from migration_neo4j.domains.file.file_domain import MigrationFile


class Folder:
    def __init__(
        self,
        name: str,
    ) -> None:
        self.name = name
        self.files: list[MigrationFile] = []
        self.subfolders: "list[Folder]" = []

    def add_file(self, file: MigrationFile) -> None:
        self.files.append(file)
        self.files.sort(key=lambda x: x.name)

    def add_subfolder(self, subfolder: "Folder") -> None:
        self.subfolders.append(subfolder)

    def search_file(self, name: str) -> MigrationFile:
        for file in self.files:
            if file.name == name:
                return file
        raise FileNotFoundError(f"file {name} not found")

    def search_subfolder(self, name: str) -> "Folder":
        for subfolder in self.subfolders:
            if subfolder.name == name:
                return subfolder
        raise FileNotFoundError(f"subfolder {name} not found")
