"""add comment parent id

Revision ID: 4b8c0f2a91d3
Revises: e60930084ea0
Create Date: 2026-05-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4b8c0f2a91d3'
down_revision = 'e60930084ea0'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('parent_id', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_comments_parent_id'), ['parent_id'], unique=False)
        batch_op.create_foreign_key(
            'fk_comments_parent_id_comments',
            'comments',
            ['parent_id'],
            ['id'],
        )


def downgrade():
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.drop_constraint('fk_comments_parent_id_comments', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_comments_parent_id'))
        batch_op.drop_column('parent_id')
