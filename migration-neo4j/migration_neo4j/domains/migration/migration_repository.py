from abc import ABC
from neo4j import GraphDatabase
from neo4j.exceptions import ResultNotSingleError


class IMigrationRepository(ABC):
    def __init__(
        self,
        uri,
        user,
        password,
    ) -> None:
        super().__init__()
        self.uri = uri
        self.user = user
        self.password = password


class MigrationRepository(IMigrationRepository):
    def __init__(
        self,
        uri,
        user,
        password,
    ) -> None:
        super().__init__(uri, user, password)
        self.driver = GraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password),
        )

    def close(self):
        self.driver.close()

    def get_current_version(self) -> str:
        with self.driver.session() as session:
            try:
                tx = session.begin_transaction()

                query = """
                MATCH (m:Migration)
                RETURN m.version, m.timestamp 
                ORDER BY m.timestamp DESC
                """
                result = tx.run(query)
                migration = result.single()
                print(migration)
                if migration is None:
                    query = """
                    CREATE (m:Migration { version: "UNKNOWN", timestamp: datetime() })
                    RETURN m.version, m.timestamp 
                    ORDER BY m.timestamp DESC
                    """
                    result = tx.run(query)
                    migration = result.single()

                if migration is None:
                    raise ValueError("is not possible to create migration node")
                tx.commit()

                return migration["m.version"]

            except ResultNotSingleError:
                raise ValueError("Not exactly one result returned, please check data")
            except Exception as e:
                raise e
            finally:
                tx.close()

    def set_current_version(self, version: str) -> None:
        with self.driver.session() as session:
            try:
                tx = session.begin_transaction()

                query = """
                MATCH (m:Migration)
                SET m.version = $version
                RETURN m.version, m.timestamp 
                ORDER BY m.timestamp DESC
                """
                result = tx.run(query, version=version)
                migration = result.single(strict=True)

                if migration is None:
                    raise ValueError("is not possible to update migration node")
                tx.commit()

            except ResultNotSingleError:
                raise ValueError("Not exactly one result returned, please check data")
            except Exception as e:
                raise e
            finally:
                tx.close()

    def execute(self, query: str, version: str) -> str:
        with self.driver.session() as session:
            try:
                tx = session.begin_transaction()
                tx.run(query)
                query = """
                MATCH (m:Migration)
                SET m.version = $version
                RETURN m.version, m.timestamp 
                ORDER BY m.timestamp DESC
                """
                result = tx.run(query, version=version)
                migration = result.single()

                if migration is None:
                    raise ValueError("is not possible to update migration node")
                tx.commit()
                return migration["m.version"]
            except Exception as e:
                raise e
            finally:
                tx.close()
