"""Add email to users

Revision ID: 002_add_email_to_users
Revises: d990ce4a7aee
Create Date: 2025-10-21 00:00:00.000000

"""
from alembic import op  # type: ignore[attr-defined]
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_email_to_users'
down_revision = 'd990ce4a7aee'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add email column to users table with unique constraint."""
    # Add email column as nullable for backward compatibility
    op.add_column('users', sa.Column('email', sa.String(), nullable=True))
    
    # Create unique index on email
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)


def downgrade() -> None:
    """Remove email column from users table."""
    # Drop index first
    op.drop_index(op.f('ix_users_email'), table_name='users')
    
    # Drop column
    op.drop_column('users', 'email')
