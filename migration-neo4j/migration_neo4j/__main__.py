from typing import Annotated, Optional
import typer
import os
from migration_neo4j.domains.folder.folder_repository import FolderRepository
from migration_neo4j.domains.file.file_repository import MigrationFileRepository
from migration_neo4j.domains.migration.migration_domain import Migration
from migration_neo4j.domains.migration.migration_repository import MigrationRepository
from dotenv import load_dotenv

app = typer.Typer()


@app.command()
def upgrade(
    env_file: Annotated[
        Optional[str],
        typer.Option(
            "--env-file",
            "-e",
            help="Path to .env file",
        ),
    ] = None,
):
    folder_repository = FolderRepository(MigrationFileRepository())
    folder_repository.write("./migrations/neo4j/versions")
    migration_folder = folder_repository.read("./migrations")

    if env_file:
        load_dotenv(env_file, encoding="utf-8")

    mirgation_repository = MigrationRepository(
        uri=os.environ["NEO4J_URI"],
        user=os.environ["NEO4J_USER"],
        password=os.environ["NEO4J_PASSWORD"],
    )

    current_version = mirgation_repository.get_current_version()
    migration = Migration(migration_folder, current_version)
    try:
        for file in migration.upgrate():
            try:
                version = mirgation_repository.execute(
                    file.content, file.sanitized_name
                )
                print(f"Migration {version} executed")
            except Exception as e:
                print(f"Error executing migration {file.sanitized_name}")
                raise e
    except ValueError as e:
        print("No migrations to execute")
        return


@app.command()
def downgrade():
    print("Downgrade")


@app.command(name="create-revision")
def create_revision():
    print("Create revision")


if __name__ == "__main__":
    app()
