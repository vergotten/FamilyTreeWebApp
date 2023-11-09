"""Added parents.

Revision ID: 3402ce49ea15
Revises: f7843fa68d3a
Create Date: 2023-11-07 21:08:13.441602

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3402ce49ea15'
down_revision = 'f7843fa68d3a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('person', schema=None) as batch_op:
        batch_op.add_column(sa.Column('mother_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('father_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(batch_op.f('fk_person_mother_id_person'), 'person', ['mother_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_person_father_id_person'), 'person', ['father_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('person', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_person_father_id_person'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('fk_person_mother_id_person'), type_='foreignkey')
        batch_op.drop_column('father_id')
        batch_op.drop_column('mother_id')

    # ### end Alembic commands ###
