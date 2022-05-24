"""organization pipeline runs

Revision ID: 8c08da3b521c
Revises: eadaab8c0d84
Create Date: 2020-10-26 14:15:14.496981

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8c08da3b521c"
down_revision = "eadaab8c0d84"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("organization_pipeline_run_post_processing_state")
    op.drop_table("organization_pipeline_run")
    op.drop_table("organization_pipeline_input_file")
    op.drop_table("post_processing_state")
    # ### end Alembic commands ###
