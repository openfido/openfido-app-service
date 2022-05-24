"""artifact_chart

Revision ID: c0de2a9adaca
Revises: a0e54652a189
Create Date: 2020-11-09 00:28:59.033914

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c0de2a9adaca'
down_revision = 'a0e54652a189'
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    op.drop_table("artifact_chart")
