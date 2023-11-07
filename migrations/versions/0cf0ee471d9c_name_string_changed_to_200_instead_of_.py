"""name string changed to 200 instead of 100.

Revision ID: 0cf0ee471d9c
Revises: 3442dbe14e00
Create Date: 2023-11-07 04:50:27.965848

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0cf0ee471d9c'
down_revision = '3442dbe14e00'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('person', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=100),
               type_=sa.String(length=200),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('person', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=sa.String(length=200),
               type_=sa.VARCHAR(length=100),
               existing_nullable=True)

    # ### end Alembic commands ###
