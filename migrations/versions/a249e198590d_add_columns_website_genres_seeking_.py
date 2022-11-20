"""Add columns (website, genres, seeking_venue, seeking_description) in Venue table

Revision ID: a249e198590d
Revises: a870fda8f4c2
Create Date: 2022-11-19 12:55:04.472214

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a249e198590d'
down_revision = 'a870fda8f4c2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('website', sa.String(length=120), nullable=True))
    op.add_column('Venue', sa.Column('genres', sa.String(length=120), nullable=True))
    op.add_column('Venue', sa.Column('seeking_venue', sa.Boolean(), nullable=True))
    op.add_column('Venue', sa.Column('seeking_description', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'seeking_description')
    op.drop_column('Venue', 'seeking_venue')
    op.drop_column('Venue', 'genres')
    op.drop_column('Venue', 'website')
    # ### end Alembic commands ###
