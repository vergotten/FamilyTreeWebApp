"""Added place_of_live, age, gender columns to Person

Revision ID: 3442dbe14e00
Revises: 134bfb4c64dd
Create Date: 2023-11-06 21:58:02.021477

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3442dbe14e00'
down_revision = '134bfb4c64dd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('person', schema=None) as batch_op:
        batch_op.add_column(sa.Column('place_of_live', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('age', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('gender', sa.String(length=120), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('person', schema=None) as batch_op:
        batch_op.drop_column('gender')
        batch_op.drop_column('age')
        batch_op.drop_column('place_of_live')

    # ### end Alembic commands ###
