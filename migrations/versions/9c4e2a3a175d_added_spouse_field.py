"""Added spouse field.

Revision ID: 9c4e2a3a175d
Revises: 42a520e871ec
Create Date: 2023-11-09 21:23:41.979788

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c4e2a3a175d'
down_revision = '42a520e871ec'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('person', schema=None) as batch_op:
        batch_op.add_column(sa.Column('spouse_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(batch_op.f('fk_person_spouse_id_person'), 'person', ['spouse_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('person', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_person_spouse_id_person'), type_='foreignkey')
        batch_op.drop_column('spouse_id')

    # ### end Alembic commands ###
