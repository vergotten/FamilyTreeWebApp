"""Added document field.

Revision ID: 6d74df2ec9f2
Revises: ffb0259775da
Create Date: 2023-11-11 22:05:31.035738

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d74df2ec9f2'
down_revision = 'ffb0259775da'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('document',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('description', sa.String(length=300), nullable=True),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('file_name', sa.String(length=120), nullable=False),
    sa.Column('comment', sa.String(length=300), nullable=True),
    sa.Column('icon', sa.String(length=120), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_document_user_id_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_document'))
    )
    op.drop_table('relationship')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('relationship',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('person1_id', sa.INTEGER(), nullable=False),
    sa.Column('person2_id', sa.INTEGER(), nullable=False),
    sa.Column('relationship_type', sa.VARCHAR(length=50), nullable=True),
    sa.ForeignKeyConstraint(['person1_id'], ['person.id'], ),
    sa.ForeignKeyConstraint(['person2_id'], ['person.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('document')
    # ### end Alembic commands ###
