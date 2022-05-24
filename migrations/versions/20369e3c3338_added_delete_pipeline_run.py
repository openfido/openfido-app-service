"""added delete pipeline run

Revision ID: 20369e3c3338
Revises: bbaf6bedc4c6
Create Date: 2021-02-09 21:58:10.037475

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20369e3c3338'
down_revision = 'bbaf6bedc4c6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('organization_workflow_pipeline_run', 'workflow_run_uuid',
               existing_type=sa.VARCHAR(length=32),
               nullable=False,
               existing_server_default=sa.text("''::character varying"))
    op.drop_column('organization_pipeline_run', 'is_deleted')
    op.alter_column('artifact_chart', 'is_deleted',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    # ### end Alembic commands ###
