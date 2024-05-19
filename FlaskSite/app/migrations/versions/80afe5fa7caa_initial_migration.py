"""Initial migration.

Revision ID: 80afe5fa7caa
Revises: 
Create Date: 2024-05-12 19:29:34.269788

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '80afe5fa7caa'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admin',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=True),
    sa.Column('time', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('subject',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('results',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('not_succes_done', sa.Boolean(), nullable=True),
    sa.Column('score', sa.Float(), nullable=True),
    sa.Column('subject_id', sa.Integer(), nullable=False),
    sa.Column('gender', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['subject_id'], ['subject.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('scores',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('result_id', sa.Integer(), nullable=False),
    sa.Column('visiting', sa.Float(), nullable=True),
    sa.Column('scores_before', sa.Float(), nullable=True),
    sa.Column('scores_before_percent', sa.Float(), nullable=True),
    sa.Column('scores_test', sa.Float(), nullable=True),
    sa.Column('test_number', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['result_id'], ['results.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('scores')
    op.drop_table('results')
    op.drop_table('subject')
    op.drop_table('admin')
    # ### end Alembic commands ###