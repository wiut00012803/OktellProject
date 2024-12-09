"""Make date_of nullable

Revision ID: 7c65d3ca4efc
Revises: 
Create Date: 2024-06-18 15:51:25.622264

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7c65d3ca4efc'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('call_info', schema=None) as batch_op:
        batch_op.alter_column('date_of',
               existing_type=sa.DATE(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('call_info', schema=None) as batch_op:
        batch_op.alter_column('date_of',
               existing_type=sa.DATE(),
               nullable=False)

    # ### end Alembic commands ###
