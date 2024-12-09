"""Add password_hash to user

Revision ID: 75eadf61b3c8
Revises: 34cd9c5e9011
Create Date: 2024-07-03 10:21:57.977495

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '75eadf61b3c8'
down_revision = '34cd9c5e9011'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('call_info', schema=None) as batch_op:
        batch_op.drop_constraint('unique_call_info', type_='unique')
        batch_op.create_unique_constraint('unique_call_info', ['phone', 'phone1', 'phone2', 'phone3', 'phone4', 'Id_chain', 'Client_id', 'fio', 'all_summ', 'summ', 'summ_dolg', 'summ_perc', 'summ_mail', 'summ_perc_plus', 'day', 'product', 'Sud_vixod', 'Sud_resh', 'region', 'adress', 'anketa', 'status_of_call', 'Try', 'result1', 'result2', 'date_of_call', 'comment', 'phone_new', 'Operator', 'date_of'])

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password_hash', sa.String(length=150), nullable=False))
        batch_op.drop_column('password')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password', sa.VARCHAR(length=150), nullable=False))
        batch_op.drop_column('password_hash')

    with op.batch_alter_table('call_info', schema=None) as batch_op:
        batch_op.drop_constraint('unique_call_info', type_='unique')
        batch_op.create_unique_constraint('unique_call_info', ['phone', 'phone1', 'phone2', 'phone3', 'phone4', 'Id_chain', 'Client_id', 'fio', 'all_summ', 'summ', 'summ_dolg', 'summ_perc', 'summ_mail', 'summ_perc_plus', 'day', 'product', 'Sud_vixod', 'Sud_resh', 'region', 'adress', 'anketa', 'status_of_call', 'Try', 'result1', 'result2', 'date_of_call', 'comment', 'phone_new', 'Operator', 'date_of', 'date_of_import'])

    # ### end Alembic commands ###
