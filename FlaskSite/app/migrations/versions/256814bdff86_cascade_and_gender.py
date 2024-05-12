"""Cascade and gender

Revision ID: 256814bdff86
Revises: 80afe5fa7caa
Create Date: 2024-05-12 19:35:06.139058

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '256814bdff86'
down_revision = '80afe5fa7caa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('results', schema=None) as batch_op:
        batch_op.alter_column('gender',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Integer(),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('results', schema=None) as batch_op:
        batch_op.alter_column('gender',
               existing_type=sa.Integer(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=False)

    # ### end Alembic commands ###
