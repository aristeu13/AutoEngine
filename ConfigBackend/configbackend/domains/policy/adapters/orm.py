import sqlalchemy as sa
from configbackend.core.orm import mapper_registry
from configbackend.domains.policy.domain.policy_model import (
    BlockType,
    ConditionType,
    WorkflowBlock,
    StartBlock,
)


workflow_block = sa.Table(
    "workflow_block",
    mapper_registry.metadata,
    sa.Column(
        "id",
        sa.Uuid(as_uuid=True, native_uuid=True),
        primary_key=True,
        server_default=sa.text("uuid_generate_v4()"),
    ),
    sa.Column("block_type", sa.Enum(BlockType), nullable=False),
    sa.Column("decision_value", sa.Boolean),
    sa.Column("field", sa.String),
    sa.Column("condition_type", sa.Enum(ConditionType)),
    sa.Column("true_workflow_block_id", sa.ForeignKey("workflow_block.id")),
    sa.Column("false_workflow_block_id", sa.ForeignKey("workflow_block.id")),
)


start_block = sa.Table(
    "start_block",
    mapper_registry.metadata,
    sa.Column(
        "id",
        sa.Uuid(as_uuid=True, native_uuid=True),
        primary_key=True,
        server_default=sa.text("uuid_generate_v4()"),
    ),
    sa.Column("workflow_block_id", sa.ForeignKey("workflow_block.id")),
)


def start_mappers():
    mapper_registry.map_imperatively(
        WorkflowBlock,
        workflow_block,
        properties={
            "true_workflow_block": sa.orm.relationship(
                WorkflowBlock,
                backref="parent_true_workflow_block",
                foreign_keys=[workflow_block.c.true_workflow_block_id],
                remote_side=[workflow_block.c.id],
            ),
            "false_workflow_block": sa.orm.relationship(
                WorkflowBlock,
                backref="parent_false_workflow_block",
                foreign_keys=[workflow_block.c.false_workflow_block_id],
                remote_side=[workflow_block.c.id],
            ),
            "start_block": sa.orm.relationship(
                StartBlock,
                backref="workflow_block",
            ),
        },
    )
    mapper_registry.map_imperatively(
        StartBlock,
        start_block,
    )
