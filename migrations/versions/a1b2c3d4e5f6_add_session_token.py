"""add session_token to users

Revision ID: a1b2c3d4e5f6
Revises: e2740d367c60
Create Date: 2026-05-13 00:00:00.000000

"""
import secrets
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = 'e2740d367c60'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('session_token', sa.String(length=32), nullable=True))
    conn = op.get_bind()
    for (uid,) in conn.execute(sa.text('SELECT id FROM users')).fetchall():
        conn.execute(sa.text('UPDATE users SET session_token = :t WHERE id = :id'),
                     {'t': secrets.token_hex(16), 'id': uid})


def downgrade():
    op.drop_column('users', 'session_token')
