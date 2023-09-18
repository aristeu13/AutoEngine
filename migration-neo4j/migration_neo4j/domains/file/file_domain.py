from typing import Annotated


LongStr = Annotated[str, "LongStr"]


class MigrationFile:
    def __init__(
        self,
        name: str,
        content: LongStr,
    ) -> None:
        if not isinstance(content, str):
            raise TypeError("content must be a string")
        if not isinstance(name, str):
            raise TypeError("name must be a string")
        if not name.endswith(".cypher"):
            raise TypeError("name must end with .cypher")

        self.name = name
        self.content = content

    @property
    def sanitized_name(self) -> str:
        return self.name.replace(".cypher", "")
