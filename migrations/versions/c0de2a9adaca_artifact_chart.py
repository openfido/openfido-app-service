"""artifact_chart

Revision ID: c0de2a9adaca
Revises: a0e54652a189
Create Date: 2020-11-09 00:28:59.033914

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector



# revision identifiers, used by Alembic.
revision = 'c0de2a9adaca'
down_revision = 'a0e54652a189'
branch_labels = None
depends_on = None

conn = op.get_bind()
inspector = Inspector.from_engine(conn)
tables = inspector.get_table_names()

def upgrade():
    if "artifact_chart" not in tables:
        op.create_table(
            "artifact_chart",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("uuid", sa.String(length=32), server_default="", nullable=False),
            sa.Column("name", sa.String(length=128), nullable=False),
            sa.Column("organization_pipeline_run_id", sa.Integer(), nullable=False),
            sa.Column(
                "artifact_uuid", sa.String(length=32), server_default="", nullable=False
            ),
            sa.Column("chart_type_code", sa.String(length=20), nullable=False),
            sa.Column("chart_config", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),


            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(
                ["organization_pipeline_run_id"],
                ["organization_pipeline_run.id"],
            ),
        )


def downgrade():
    op.drop_table("artifact_chart")
