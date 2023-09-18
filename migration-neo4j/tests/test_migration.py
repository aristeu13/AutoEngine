import pytest
from migration_neo4j.domains.folder.folder_repository import (
    FolderRepositoryMock,
    IFolderRepository,
    Folder,
)
from migration_neo4j.domains.file.file_repository import (
    MigrationFileRepositoryMock,
    IMigrationFileRepository,
    MigrationFile,
)
from migration_neo4j.domains.migration.migration_domain import Migration


@pytest.fixture
def file_r():
    repo = MigrationFileRepositoryMock()
    repo.storage.reset()
    yield repo
    repo.storage.reset()


@pytest.fixture
def folder_r(
    file_r: IMigrationFileRepository,
):
    repo = FolderRepositoryMock(file_r)
    repo.storage.reset()
    yield repo
    repo.storage.reset()


def test_raised_error_in_migration(
    folder_r: IFolderRepository,
    file_r: IMigrationFileRepository,
):
    file_r.write(
        "./other_name/neo4j/versions/v1.0.0.cypher",
        MigrationFile(
            "v1.0.0.cypher", 'CREATE (Emil:Person {name:"Emil Eifrem", born:1978})'
        ),
    )

    migration_folder = folder_r.read("other_name")

    with pytest.raises(ValueError):
        Migration(migration_folder, "UNKNOWN")

    file_r.write(
        "./migrations/other_name/versions/v1.0.1.cypher",
        MigrationFile(
            "v1.0.1.cypher", 'CREATE (Teu:Person {name:"Teu Eifrem", born:1998})'
        ),
    )
    migration_folder = folder_r.read("migrations")

    with pytest.raises(ValueError):
        Migration(migration_folder, "UNKNOWN")

    file_r.write(
        "./migrations/neo4j/others/v1.0.1.cypher",
        MigrationFile(
            "v1.0.1.cypher", 'CREATE (Teu:Person {name:"Teu Eifrem", born:1998})'
        ),
    )
    migration_folder = folder_r.read("migrations")
    with pytest.raises(ValueError):
        Migration(migration_folder, "UNKNOWN")


def test_first_migration(
    folder_r: IFolderRepository,
    file_r: IMigrationFileRepository,
):
    file_r.write(
        "./migrations/neo4j/versions/v1.0.0.cypher",
        MigrationFile(
            "v1.0.0.cypher", 'CREATE (Emil:Person {name:"Emil Eifrem", born:1978})'
        ),
    )
    file_r.write(
        "./migrations/neo4j/versions/v1.0.1.cypher",
        MigrationFile(
            "v1.0.1.cypher", 'CREATE (Teu:Person {name:"Teu Eifrem", born:1998})'
        ),
    )
    migration_folder = folder_r.read("migrations")

    migration = Migration(migration_folder, "UNKNOWN")
    assert migration.current_version == "UNKNOWN"
    assert migration.migration_folder.name == "migrations"
    assert len(migration.migrations_files) == 2

    test_data = [
        (
            "v1.0.0.cypher",
            "v1.0.0",
            'CREATE (Emil:Person {name:"Emil Eifrem", born:1978})',
        ),
        (
            "v1.0.1.cypher",
            "v1.0.1",
            'CREATE (Teu:Person {name:"Teu Eifrem", born:1998})',
        ),
    ]
    for file in migration.upgrate():
        test = test_data.pop(0)
        assert isinstance(file, MigrationFile)
        assert file.name == test[0]
        assert file.sanitized_name == test[1]
        assert file.content == test[2]
    assert len(test_data) == 0

    assert migration.current_version == "v1.0.1"


def test_second_migration(
    folder_r: IFolderRepository,
    file_r: IMigrationFileRepository,
):
    file_r.write(
        "./migrations/neo4j/versions/v1.0.0.cypher",
        MigrationFile(
            "v1.0.0.cypher", 'CREATE (Emil:Person {name:"Emil Eifrem", born:1978})'
        ),
    )
    file_r.write(
        "./migrations/neo4j/versions/v1.0.1.cypher",
        MigrationFile(
            "v1.0.1.cypher", 'CREATE (Teu:Person {name:"Teu Eifrem", born:1998})'
        ),
    )

    file_r.write(
        "./migrations/neo4j/versions/v1.0.2.cypher",
        MigrationFile(
            "v1.0.2.cypher", 'CREATE (Teu:Person {name:"Teu Eifrem", born:2000})'
        ),
    )

    migration_folder = folder_r.read("migrations")

    migration = Migration(migration_folder, "v1.0.1")
    assert migration.current_version == "v1.0.1"
    assert migration.migration_folder.name == "migrations"
    assert len(migration.migrations_files) == 3

    test_data = [
        (
            "v1.0.2.cypher",
            "v1.0.2",
            'CREATE (Teu:Person {name:"Teu Eifrem", born:2000})',
        ),
    ]
    for file in migration.upgrate():
        test = test_data.pop(0)
        assert isinstance(file, MigrationFile)
        assert file.name == test[0]
        assert file.sanitized_name == test[1]
        assert file.content == test[2]


def test_lasted_migration(
    folder_r: IFolderRepository,
    file_r: IMigrationFileRepository,
):
    file_r.write(
        "./migrations/neo4j/versions/v1.0.0.cypher",
        MigrationFile(
            "v1.0.0.cypher", 'CREATE (Emil:Person {name:"Emil Eifrem", born:1978})'
        ),
    )
    file_r.write(
        "./migrations/neo4j/versions/v1.0.1.cypher",
        MigrationFile(
            "v1.0.1.cypher", 'CREATE (Teu:Person {name:"Teu Eifrem", born:1998})'
        ),
    )

    file_r.write(
        "./migrations/neo4j/versions/v1.0.2.cypher",
        MigrationFile(
            "v1.0.2.cypher", 'CREATE (Teu:Person {name:"Teu Eifrem", born:2000})'
        ),
    )

    migration_folder = folder_r.read("migrations")

    migration = Migration(migration_folder, "v1.0.2")
    assert migration.current_version == "v1.0.2"
    assert migration.migration_folder.name == "migrations"
    assert len(migration.migrations_files) == 3

    with pytest.raises(ValueError):
        for _ in migration.upgrate():
            pass


def test_migration_not_found(
    folder_r: IFolderRepository,
    file_r: IMigrationFileRepository,
):
    file_r.write(
        "./migrations/neo4j/versions/v1.0.0.cypher",
        MigrationFile(
            "v1.0.0.cypher", 'CREATE (Emil:Person {name:"Emil Eifrem", born:1978})'
        ),
    )
    file_r.write(
        "./migrations/neo4j/versions/v1.0.1.cypher",
        MigrationFile(
            "v1.0.1.cypher", 'CREATE (Teu:Person {name:"Teu Eifrem", born:1998})'
        ),
    )

    file_r.write(
        "./migrations/neo4j/versions/v1.0.2.cypher",
        MigrationFile(
            "v1.0.2.cypher", 'CREATE (Teu:Person {name:"Teu Eifrem", born:2000})'
        ),
    )

    migration_folder = folder_r.read("migrations")

    migration = Migration(migration_folder, "not_found")
    assert migration.current_version == "not_found"
    assert migration.migration_folder.name == "migrations"
    assert len(migration.migrations_files) == 3

    with pytest.raises(ValueError):
        for _ in migration.upgrate():
            pass
