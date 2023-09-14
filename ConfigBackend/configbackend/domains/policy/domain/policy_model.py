from enum import Enum
from typing import Annotated
from uuid import UUID


class BlockType(Enum):
    END = "END"
    DECISION = "DECISION"


class ConditionType(Enum):
    EQ = "EQ"
    GT = "GT"
    GE = "GE"
    LT = "LT"
    LE = "LE"


ImplicitId = Annotated[UUID, "ID inferred from the database"]


class WorkflowBlock:
    id: ImplicitId
    start_block: "StartBlock | None"

    def __init__(
        self,
        block_type: BlockType,
        decision_value: bool | None = None,
        field: str | None = None,
        condition_type: ConditionType | None = None,
        true_workflow_block: "WorkflowBlock | None" = None,
        false_workflow_block: "WorkflowBlock | None" = None,
    ) -> None:
        self.block_type = block_type
        self.decision_value = decision_value
        self.field = field
        self.condition_type = condition_type
        self.true_workflow_block = true_workflow_block
        self.false_workflow_block = false_workflow_block


class StartBlock:
    id: ImplicitId

    def __init__(
        self,
        workflow_block: WorkflowBlock,
    ) -> None:
        self.workflow_block = workflow_block
