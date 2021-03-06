"""empty message

Revision ID: ecb323cc445f
Revises: cf1db10099c1
Create Date: 2021-06-14 12:57:34.019665

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ecb323cc445f'
down_revision = 'cf1db10099c1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('slider',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pagetitle', sa.String(length=100), nullable=True),
    sa.Column('description', sa.String(length=100), nullable=True),
    sa.Column('image', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('slider')
    # ### end Alembic commands ###
