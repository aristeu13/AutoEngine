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


def test_write_folder(
    folder_r: IFolderRepository,
    file_r: IMigrationFileRepository,
):
    folder_r.write("tests/test_folder")

    folder = folder_r.read("tests/test_folder")

    assert folder.name == "test_folder"
    assert isinstance(folder, Folder)
    assert len(folder.files) == 0
    assert len(folder.subfolders) == 0


def test_write_folder_with_file(
    folder_r: IFolderRepository,
    file_r: IMigrationFileRepository,
):
    folder_r.write("tests/test_folder")
    file_r.write(
        "tests/test_folder/test_file.cypher",
        MigrationFile(
            "test_file.cypher", 'CREATE (Emil:Person {name:"Emil Eifrem", born:1978})'
        ),
    )
    file = file_r.read("tests/test_folder/test_file.cypher")
    assert file.name == "test_file.cypher"
    assert file.sanitized_name == "test_file"
    assert file.content == 'CREATE (Emil:Person {name:"Emil Eifrem", born:1978})'

    folder = folder_r.read("tests/test_folder")

    assert folder.name == "test_folder"
    assert isinstance(folder, Folder)
    assert len(folder.files) == 1
    assert len(folder.subfolders) == 0


def test_write_folder_with_folder(
    folder_r: IFolderRepository,
):
    folder_r.write("tests/test_folder")
    folder_r.write("tests/test_folder/test_subfolder")

    folder = folder_r.read("tests/test_folder")

    assert folder.name == "test_folder"
    assert isinstance(folder, Folder)
    assert len(folder.files) == 0
    assert len(folder.subfolders) == 1

    subfolder = folder.subfolders[0]
    assert subfolder.name == "test_subfolder"
    assert isinstance(subfolder, Folder)
    assert len(subfolder.files) == 0
    assert len(subfolder.subfolders) == 0


def test_write_folder_and_not_found_file(
    folder_r: IFolderRepository,
    file_r: IMigrationFileRepository,
):
    folder_r.write("tests/test_folder")
    with pytest.raises(FileNotFoundError):
        file_r.read("tests/test_folder/test_file.cypher")
    with pytest.raises(TypeError):
        file_r.read("tests/test_folder")


def test_write_file_and_not_found_folder(
    folder_r: IFolderRepository,
    file_r: IMigrationFileRepository,
):
    file_r.write(
        "tests/test_folder/test_file.cypher",
        MigrationFile(
            "test_file.cypher", 'CREATE (Emil:Person {name:"Emil Eifrem", born:1978})'
        ),
    )
    with pytest.raises(NotADirectoryError):
        folder_r.read("tests/test_folder/test_file")
    with pytest.raises(NotADirectoryError):
        folder_r.read("tests/test_folder/test_file.cypher")


def test_raised_not_str_in_migration_file():
    with pytest.raises(TypeError):
        MigrationFile(
            name="test_file.cypher",
            content=123,
        )
    with pytest.raises(TypeError):
        MigrationFile(
            name=123,
            content='CREATE (Emil:Person {name:"Emil Eifrem", born:1978})',
        )


def test_raised_file_extension():
    with pytest.raises(TypeError):
        MigrationFile(
            name="test_file",
            content='CREATE (Emil:Person {name:"Emil Eifrem", born:1978})',
        )


def test_search_files_in_folder(
    file_r: IMigrationFileRepository,
    folder_r: IFolderRepository,
):
    file_r.write(
        "tests/test_folder/test_file.cypher",
        MigrationFile(
            "test_file.cypher", 'CREATE (Emil:Person {name:"Emil Eifrem", born:1978})'
        ),
    )

    folder = folder_r.read("tests/test_folder")

    file = folder.search_file("test_file.cypher")

    assert file.name == "test_file.cypher"
    assert file.sanitized_name == "test_file"
    assert file.content == 'CREATE (Emil:Person {name:"Emil Eifrem", born:1978})'
    assert isinstance(file, MigrationFile)


def test_search_folders_in_folder(
    folder_r: IFolderRepository,
):
    folder_r.write("tests/test_folder/test_subfolder")

    folder = folder_r.read("tests/test_folder")

    subfolder = folder.search_subfolder("test_subfolder")

    assert subfolder.name == "test_subfolder"
    assert isinstance(subfolder, Folder)
    assert len(subfolder.files) == 0
    assert len(subfolder.subfolders) == 0


def test_raised_search(
    folder_r: IFolderRepository,
    file_r: IMigrationFileRepository,
):
    file_r.write(
        "tests/test_folder/test_file.cypher",
        MigrationFile(
            "test_file.cypher", 'CREATE (Emil:Person {name:"Emil Eifrem", born:1978})'
        ),
    )

    folder = folder_r.read("tests/test_folder")

    with pytest.raises(FileNotFoundError):
        folder.search_file("test_file")
    with pytest.raises(FileNotFoundError):
        folder.search_subfolder("test_subfolder")
