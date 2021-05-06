"""empty message

Revision ID: 25189d391e54
Revises: 
Create Date: 2021-05-06 18:17:25.684552

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '25189d391e54'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cancellation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('day_of_the_week', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('group',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('group_id', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('superuser',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('superuser')
    op.drop_table('group')
    op.drop_table('cancellation')
    # ### end Alembic commands ###