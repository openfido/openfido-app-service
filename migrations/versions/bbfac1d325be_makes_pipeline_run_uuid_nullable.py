"""makes_pipeline_run_uuid_nullable

Revision ID: bbfac1d325be
Revises: f9899ada778b
Create Date: 2020-11-04 00:02:22.790415

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = 'bbfac1d325be'
down_revision = 'f9899ada778b'
branch_labels = None
depends_on = None

conn = op.get_bind()
inspector = Inspector.from_engine(conn)
tables = inspector.get_table_names()

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    if table_name not in tables:
        op.alter_column('organization_pipeline_run', 'pipeline_run_uuid',
                existing_type=sa.VARCHAR(length=32),
                nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('organization_pipeline_run', 'pipeline_run_uuid',
               existing_type=sa.VARCHAR(length=32),
               nullable=False)
    # ### end Alembic commands ###
