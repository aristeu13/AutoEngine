from migration_neo4j.domains.folder.folder_domain import Folder, MigrationFile

FIRST_MIGRATION = "UNKNOWN"


class Migration:
    def __init__(
        self,
        migration_folder: Folder,
        current_version: str,
    ) -> None:
        if migration_folder.name != "migrations":
            raise ValueError("migration_folder must be called migrations")

        try:
            neo4j_folder = migration_folder.search_subfolder("neo4j")
        except FileNotFoundError as e:
            raise ValueError("neo4j folder not found inside migrations folder") from e

        try:
            versions_folder = neo4j_folder.search_subfolder("versions")
        except FileNotFoundError as e:
            raise ValueError("versions folder not found inside neo4j folder") from e

        self.migration_folder = migration_folder
        self.current_version = current_version
        self.migrations_files = versions_folder.files

    def _get_index_current_version(self) -> int:
        if self.current_version == FIRST_MIGRATION:  # first migration
            return -1

        for index, file in enumerate(self.migrations_files):
            if file.sanitized_name == self.current_version:
                return index
        raise ValueError(f"current_version {self.current_version} not found")

    def upgrate(self):
        index_current_version = self._get_index_current_version()
        # check if current_version is the last version
        if index_current_version == len(self.migrations_files) - 1:
            raise ValueError("current_version is the last version")
        for file in self.migrations_files[index_current_version + 1 :]:
            yield file
            self.current_version = file.sanitized_name
