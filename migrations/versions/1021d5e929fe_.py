"""empty message

Revision ID: 1021d5e929fe
Revises: d99229a2d816
Create Date: 2021-07-19 14:37:04.977675

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1021d5e929fe'
down_revision = 'd99229a2d816'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('gencode',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('count', sa.Integer(), nullable=True),
    sa.Column('group', sa.String(length=50), nullable=True),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('count_used', sa.Integer(), nullable=True),
    sa.Column('count_number', sa.Integer(), nullable=True),
    sa.Column('proccur', sa.String(length=50), nullable=True),
    sa.Column('count_sibol', sa.Integer(), nullable=True),
    sa.Column('datedown', sa.String(length=50), nullable=True),
    sa.Column('code', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('group',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('comment', sa.String(length=200), nullable=True),
    sa.Column('sum_count', sa.Integer(), nullable=True),
    sa.Column('active', sa.Integer(), nullable=True),
    sa.Column('used', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('group')
    op.drop_table('gencode')
    # ### end Alembic commands ###