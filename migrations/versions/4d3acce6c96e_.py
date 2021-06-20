"""empty message

Revision ID: 4d3acce6c96e
Revises: ecb323cc445f
Create Date: 2021-06-17 11:57:27.756926

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4d3acce6c96e'
down_revision = 'ecb323cc445f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product', sa.Column('image2', sa.String(length=100), nullable=True))
    op.add_column('product', sa.Column('image3', sa.String(length=100), nullable=True))
    op.add_column('product', sa.Column('image4', sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('product', 'image4')
    op.drop_column('product', 'image3')
    op.drop_column('product', 'image2')
    # ### end Alembic commands ###